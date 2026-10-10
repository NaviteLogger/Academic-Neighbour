import { Injectable, inject, signal } from '@angular/core';
import { Subject, timer } from 'rxjs';
import { environment } from '../../environments/environment';
import { Message } from '../models/conversation.model';
import { AuthService } from './auth.service';

/**
 * WebSocket message types
 */
export enum WebSocketMessageType {
    CONNECTION = 'connection',
    MESSAGE = 'message',
    USER_LEFT = 'user_left',
    ERROR = 'error'
}

/**
 * WebSocket message interface
 */
export interface WebSocketMessage {
    type: WebSocketMessageType;
    id?: number;
    content?: string;
    sender_id?: number;
    sender_name?: string;
    conversation_id?: number;
    created_at?: string;
    status?: string;
    user_id?: number;
    username?: string;
    message?: string;
}

/**
 * WebSocket connection status
 */
export enum ConnectionStatus {
    DISCONNECTED = 'disconnected',
    CONNECTING = 'connecting',
    CONNECTED = 'connected',
    ERROR = 'error'
}

@Injectable({
    providedIn: 'root',
})
export class WebSocketService {
    private authService = inject(AuthService);
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectDelay = 2000; // 2 seconds
    private currentConversationId: number | null = null;

    // Signals for reactive state
    connectionStatus = signal<ConnectionStatus>(ConnectionStatus.DISCONNECTED);

    // Subjects for message streams
    private messageSubject = new Subject<Message>();
    private errorSubject = new Subject<string>();
    private connectionSubject = new Subject<WebSocketMessage>();
    private userLeftSubject = new Subject<{ user_id: number; username: string }>();

    // Observable streams
    messages$ = this.messageSubject.asObservable();
    errors$ = this.errorSubject.asObservable();
    connection$ = this.connectionSubject.asObservable();
    userLeft$ = this.userLeftSubject.asObservable();

    /**
     * Connect to a conversation's WebSocket
     */
    connect(conversationId: number): void {
        // Disconnect any existing connection
        this.disconnect();

        const token = this.authService.getToken();
        if (!token) {
            this.errorSubject.next('No authentication token available');
            this.connectionStatus.set(ConnectionStatus.ERROR);
            return;
        }

        this.currentConversationId = conversationId;
        this.connectionStatus.set(ConnectionStatus.CONNECTING);

        // Convert http/https to ws/wss
        const wsProtocol = environment.apiUrl.startsWith('https') ? 'wss' : 'ws';
        const wsBaseUrl = environment.apiUrl.replace(/^https?:\/\//, '');
        const wsUrl = `${wsProtocol}://${wsBaseUrl}/conversations/${conversationId}/ws?token=${token}`;

        try {
            this.ws = new WebSocket(wsUrl);
            this.setupWebSocketHandlers();
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.connectionStatus.set(ConnectionStatus.ERROR);
            this.errorSubject.next('Failed to create WebSocket connection');
        }
    }

    /**
     * Setup WebSocket event handlers
     */
    private setupWebSocketHandlers(): void {
        if (!this.ws) return;

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.connectionStatus.set(ConnectionStatus.CONNECTED);
            this.reconnectAttempts = 0;
        };

        this.ws.onmessage = (event) => {
            try {
                const data: WebSocketMessage = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.connectionStatus.set(ConnectionStatus.ERROR);
            this.errorSubject.next('WebSocket connection error');
        };

        this.ws.onclose = (event) => {
            console.log('WebSocket closed:', event.code, event.reason);
            this.connectionStatus.set(ConnectionStatus.DISCONNECTED);

            // Handle different close codes
            if (event.code === 4000 || event.code === 4001) {
                this.errorSubject.next('Authentication error. Please login again.');
            } else if (event.code === 4003) {
                this.errorSubject.next('Not authorized to access this conversation.');
            } else if (event.code === 4004) {
                this.errorSubject.next('Conversation not found.');
            } else if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                // Attempt reconnection for non-normal closures
                this.attemptReconnect();
            }
        };
    }

    /**
     * Handle incoming WebSocket messages
     */
    private handleWebSocketMessage(data: WebSocketMessage): void {
        switch (data.type) {
            case WebSocketMessageType.CONNECTION:
                console.log('Connection confirmed:', data);
                this.connectionSubject.next(data);
                break;

            case WebSocketMessageType.MESSAGE:
                if (data.id && data.content && data.sender_id && data.sender_name && data.created_at) {
                    const message: Message = {
                        id: data.id,
                        content: data.content,
                        sender_id: data.sender_id,
                        sender_name: data.sender_name,
                        conversation_id: data.conversation_id!,
                        created_at: data.created_at
                    };
                    this.messageSubject.next(message);
                }
                break;

            case WebSocketMessageType.USER_LEFT:
                if (data.user_id && data.username) {
                    this.userLeftSubject.next({
                        user_id: data.user_id,
                        username: data.username
                    });
                }
                break;

            case WebSocketMessageType.ERROR:
                this.errorSubject.next(data.message || 'Unknown error');
                break;

            default:
                console.warn('Unknown WebSocket message type:', data);
        }
    }

    /**
     * Send a message through WebSocket
     */
    sendMessage(content: string): void {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.errorSubject.next('WebSocket is not connected');
            return;
        }

        try {
            this.ws.send(JSON.stringify({ content }));
        } catch (error) {
            console.error('Failed to send message:', error);
            this.errorSubject.next('Failed to send message');
        }
    }

    /**
     * Disconnect WebSocket
     */
    disconnect(): void {
        if (this.ws) {
            this.ws.close(1000, 'Client disconnecting');
            this.ws = null;
        }
        this.currentConversationId = null;
        this.connectionStatus.set(ConnectionStatus.DISCONNECTED);
        this.reconnectAttempts = 0;
    }

    /**
     * Attempt to reconnect to WebSocket
     */
    private attemptReconnect(): void {
        if (!this.currentConversationId || this.reconnectAttempts >= this.maxReconnectAttempts) {
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff

        console.log(`Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms...`);

        timer(delay).subscribe(() => {
            if (this.currentConversationId) {
                this.connect(this.currentConversationId);
            }
        });
    }

    /**
     * Check if WebSocket is connected
     */
    isConnected(): boolean {
        return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
    }

    /**
     * Get current connection status
     */
    getStatus(): ConnectionStatus {
        return this.connectionStatus();
    }
}
