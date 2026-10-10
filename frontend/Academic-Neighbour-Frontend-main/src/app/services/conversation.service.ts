import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { User } from '../models/auth.model';
import { Conversation, ConversationCreate, Message, MessageCreate } from '../models/conversation.model';

@Injectable({
    providedIn: 'root',
})
export class ConversationService {
    private http = inject(HttpClient);
    private readonly apiUrl = environment.apiUrl;

    /**
     * Get all conversations the current user is part of
     */
    getConversations(): Observable<Conversation[]> {
        return this.http.get<Conversation[]>(`${this.apiUrl}/conversations/`).pipe(
            catchError(error => {
                console.error('Failed to fetch conversations:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get a specific conversation by ID
     */
    getConversation(conversationId: number): Observable<Conversation> {
        return this.http.get<Conversation>(`${this.apiUrl}/conversations/${conversationId}`).pipe(
            catchError(error => {
                console.error('Failed to fetch conversation:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Create a new conversation
     */
    createConversation(conversation: ConversationCreate): Observable<Conversation> {
        return this.http.post<Conversation>(`${this.apiUrl}/conversations/`, conversation).pipe(
            catchError(error => {
                console.error('Failed to create conversation:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get all participants in a conversation
     */
    getParticipants(conversationId: number): Observable<User[]> {
        return this.http.get<User[]>(`${this.apiUrl}/conversations/${conversationId}/participants`).pipe(
            catchError(error => {
                console.error('Failed to fetch participants:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get all messages in a conversation
     */
    getMessages(conversationId: number): Observable<Message[]> {
        return this.http.get<Message[]>(`${this.apiUrl}/conversations/${conversationId}/messages`).pipe(
            catchError(error => {
                console.error('Failed to fetch messages:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Send a message to a conversation
     */
    sendMessage(conversationId: number, message: MessageCreate): Observable<Message> {
        return this.http.post<Message>(`${this.apiUrl}/conversations/${conversationId}/messages`, message).pipe(
            catchError(error => {
                console.error('Failed to send message:', error);
                return throwError(() => error);
            })
        );
    }
}
