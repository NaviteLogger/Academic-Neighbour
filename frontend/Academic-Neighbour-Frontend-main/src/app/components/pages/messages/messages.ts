import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit, computed, effect, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatBadgeModule } from '@angular/material/badge';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatListModule } from '@angular/material/list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Subscription } from 'rxjs';
import { UserRead } from '../../../models/auth.model';
import { Conversation, Message } from '../../../models/conversation.model';
import { AuthService } from '../../../services/auth.service';
import { ConversationService } from '../../../services/conversation.service';
import { FriendshipService } from '../../../services/friendship.service';
import { ConnectionStatus, WebSocketService } from '../../../services/websocket.service';
import { FeedHeaderComponent } from '../feed/feed-header/feed-header';

@Component({
    selector: 'app-messages',
    standalone: true,
    imports: [
        CommonModule,
        FormsModule,
        MatIconModule,
        MatButtonModule,
        MatFormFieldModule,
        MatInputModule,
        MatListModule,
        MatBadgeModule,
        MatProgressSpinnerModule,
        MatTooltipModule,
        MatTabsModule,
        FeedHeaderComponent
    ],
    templateUrl: './messages.html',
    styleUrl: './messages.css',
})
export class MessagesPage implements OnInit, OnDestroy {
    private conversationService = inject(ConversationService);
    private wsService = inject(WebSocketService);
    private authService = inject(AuthService);
    private friendshipService = inject(FriendshipService);

    // State signals
    conversations = signal<Conversation[]>([]);
    friends = signal<UserRead[]>([]);
    selectedConversation = signal<Conversation | null>(null);
    selectedFriend = signal<UserRead | null>(null);
    messages = signal<Message[]>([]);
    messageInput = signal<string>('');
    activeTab = signal<'conversations' | 'friends'>('conversations');
    isLoadingConversations = signal<boolean>(false);
    isLoadingFriends = signal<boolean>(false);
    isLoadingMessages = signal<boolean>(false);
    isSendingMessage = signal<boolean>(false);
    isCreatingConversation = signal<boolean>(false);

    // WebSocket connection status
    readonly connectionStatus = this.wsService.connectionStatus;
    readonly currentUser = this.authService.currentUser;

    // Computed values
    readonly isConnected = computed(() =>
        this.connectionStatus() === ConnectionStatus.CONNECTED
    );
    readonly isConnecting = computed(() =>
        this.connectionStatus() === ConnectionStatus.CONNECTING
    );
    readonly hasSelectedConversation = computed(() =>
        this.selectedConversation() !== null
    );

    // Expose enum to template
    readonly ConnectionStatus = ConnectionStatus;

    // Subscriptions
    private subscriptions: Subscription[] = [];

    constructor() {
        // Auto-scroll to bottom when new messages arrive
        effect(() => {
            const msgs = this.messages();
            if (msgs.length > 0) {
                setTimeout(() => this.scrollToBottom(), 100);
            }
        });
    }

    ngOnInit(): void {
        this.loadConversations();
        this.loadFriends();
        this.setupWebSocketSubscriptions();
    }

    ngOnDestroy(): void {
        this.wsService.disconnect();
        this.subscriptions.forEach(sub => sub.unsubscribe());
    }

    /**
     * Setup WebSocket message subscriptions
     */
    private setupWebSocketSubscriptions(): void {
        // Subscribe to incoming messages
        this.subscriptions.push(
            this.wsService.messages$.subscribe((message) => {
                console.log('Received WebSocket message:', message);
                // Only add message if it's for the currently selected conversation
                const selectedConv = this.selectedConversation();
                if (selectedConv && message.conversation_id === selectedConv.id) {
                    // Check if message already exists to avoid duplicates
                    const exists = this.messages().some(m => m.id === message.id);
                    if (!exists) {
                        this.messages.update(msgs => [...msgs, message]);
                    }
                }
            })
        );

        // Subscribe to errors
        this.subscriptions.push(
            this.wsService.errors$.subscribe((error) => {
                console.error('WebSocket error:', error);
                alert(error);
            })
        );

        // Subscribe to user left events
        this.subscriptions.push(
            this.wsService.userLeft$.subscribe((data) => {
                console.log(`User ${data.username} left the conversation`);
            })
        );
    }

    /**
     * Load all conversations and their participants
     */
    loadConversations(): void {
        this.isLoadingConversations.set(true);
        this.conversationService.getConversations().subscribe({
            next: (conversations) => {
                console.log('Loaded conversations:', conversations);

                // For each conversation, fetch participants and set display name
                const currentUserId = this.currentUser()?.id;
                conversations.forEach(conv => {
                    this.conversationService.getParticipants(conv.id).subscribe({
                        next: (participants) => {
                            // Store participants in the conversation object
                            conv.participants = participants.map(p => ({
                                id: p.id,
                                username: p.username,
                                first_name: p.first_name || '',
                                last_name: p.last_name || ''
                            }));

                            // Find the other participant (not the current user)
                            const otherParticipant = participants.find(p => p.id !== currentUserId);
                            if (otherParticipant) {
                                const displayName = `${otherParticipant.first_name} ${otherParticipant.last_name}`.trim()
                                    || otherParticipant.username;
                                conv.displayName = displayName;
                            } else {
                                conv.displayName = conv.title;
                            }
                        },
                        error: (error) => {
                            console.error('Error loading participants for conversation', conv.id, error);
                            conv.displayName = conv.title;
                        }
                    });
                });

                // Note: The backend should prevent duplicates, but we'll keep all conversations for now
                // since they might have different message histories
                this.conversations.set(conversations);
                this.isLoadingConversations.set(false);
            },
            error: (error) => {
                console.error('Error loading conversations:', error);
                this.isLoadingConversations.set(false);
            }
        });
    }

    /**
     * Load all friends
     */
    loadFriends(): void {
        this.isLoadingFriends.set(true);
        this.friendshipService.getAcceptedFriends().subscribe({
            next: (friends) => {
                this.friends.set(friends);
                this.isLoadingFriends.set(false);
            },
            error: (error) => {
                console.error('Error loading friends:', error);
                this.isLoadingFriends.set(false);
            }
        });
    }

    /**
     * Select a conversation and load its messages
     */
    selectConversation(conversation: Conversation): void {
        // Disconnect from previous conversation
        if (this.wsService.isConnected()) {
            this.wsService.disconnect();
        }

        this.selectedConversation.set(conversation);
        this.loadMessages(conversation.id);

        // Connect to WebSocket for real-time updates
        this.wsService.connect(conversation.id);
    }

    /**
     * Select a friend and start a conversation
     */
    selectFriend(friend: UserRead): void {
        this.selectedFriend.set(friend);

        // First, check if a conversation with this friend already exists
        const existingConversation = this.findConversationWithUser(friend.id);

        if (existingConversation) {
            console.log('Found existing conversation with friend:', existingConversation);
            // Switch to conversations tab and select the existing conversation
            this.activeTab.set('conversations');
            this.selectedFriend.set(null);
            this.selectConversation(existingConversation);
            return;
        }

        // No existing conversation found, create a new one
        this.isCreatingConversation.set(true);

        this.conversationService.createConversation({
            participant_id: friend.id
        }).subscribe({
            next: (conversation) => {
                console.log('Created new conversation:', conversation);
                this.isCreatingConversation.set(false);

                // Add to conversations list
                this.conversations.update(convs => [conversation, ...convs]);

                // Fetch participants for the new conversation to set displayName
                const currentUserId = this.currentUser()?.id;
                this.conversationService.getParticipants(conversation.id).subscribe({
                    next: (participants) => {
                        const otherParticipant = participants.find(p => p.id !== currentUserId);
                        if (otherParticipant) {
                            const displayName = `${otherParticipant.first_name} ${otherParticipant.last_name}`.trim()
                                || otherParticipant.username;
                            conversation.displayName = displayName;
                            // Update the conversation in the list
                            this.conversations.update(convs =>
                                convs.map(c => c.id === conversation.id ? conversation : c)
                            );
                        }
                    }
                });

                // Switch to conversations tab and select the conversation
                this.activeTab.set('conversations');
                this.selectedFriend.set(null);
                this.selectConversation(conversation);
            },
            error: (error) => {
                console.error('Error creating conversation:', error);
                this.isCreatingConversation.set(false);
                alert('Nie udało się rozpocząć rozmowy');
            }
        });
    }

    /**
     * Find a conversation that includes a specific user
     */
    private findConversationWithUser(userId: number): Conversation | null {
        const currentUserId = this.currentUser()?.id;
        if (!currentUserId) return null;

        // Check if any conversation has participants that include both the current user and the target user
        for (const conv of this.conversations()) {
            if (conv.participants && conv.participants.length === 2) {
                const participantIds = conv.participants.map(p => p.id);
                if (participantIds.includes(currentUserId) && participantIds.includes(userId)) {
                    return conv;
                }
            }
        }
        return null;
    }

    /**
     * Load messages for a conversation
     */
    private loadMessages(conversationId: number): void {
        this.isLoadingMessages.set(true);
        this.conversationService.getMessages(conversationId).subscribe({
            next: (messages) => {
                this.messages.set(messages);
                this.isLoadingMessages.set(false);
            },
            error: (error) => {
                console.error('Error loading messages:', error);
                this.isLoadingMessages.set(false);
            }
        });
    }

    /**
     * Send a message
     */
    sendMessage(): void {
        const content = this.messageInput().trim();
        const conversation = this.selectedConversation();

        if (!content || !conversation) return;

        // If WebSocket is connected, send via WebSocket
        if (this.wsService.isConnected()) {
            console.log('Sending message via WebSocket:', content);
            this.wsService.sendMessage(content);
            this.messageInput.set('');
            // Note: The message will be added to the UI when we receive it back from the WebSocket
        } else {
            // Fallback to REST API
            console.log('WebSocket not connected, sending via REST API');
            this.sendMessageViaREST(conversation.id, content);
        }
    }

    /**
     * Send message via REST API (fallback)
     */
    private sendMessageViaREST(conversationId: number, content: string): void {
        this.isSendingMessage.set(true);
        this.conversationService.sendMessage(conversationId, { content }).subscribe({
            next: (message) => {
                this.messages.update(msgs => [...msgs, message]);
                this.messageInput.set('');
                this.isSendingMessage.set(false);
            },
            error: (error) => {
                console.error('Error sending message:', error);
                alert('Nie udało się wysłać wiadomości');
                this.isSendingMessage.set(false);
            }
        });
    }

    /**
     * Handle tab change
     */
    onTabChange(index: number): void {
        this.activeTab.set(index === 0 ? 'conversations' : 'friends');
    }

    /**
     * Format date for display
     */
    formatDate(dateString: string): string {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'Teraz';
        if (diffMins < 60) return `${diffMins}min temu`;
        if (diffHours < 24) return `${diffHours}h temu`;
        if (diffDays < 7) return `${diffDays}d temu`;

        return date.toLocaleDateString('pl-PL', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Format time for message
     */
    formatTime(dateString: string): string {
        const date = new Date(dateString);
        return date.toLocaleTimeString('pl-PL', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Check if message is from current user
     */
    isMyMessage(message: Message): boolean {
        const user = this.currentUser();
        return user ? message.sender_id === user.id : false;
    }

    /**
     * Get initials from name
     */
    getInitials(name: string): string {
        return name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2);
    }

    /**
     * Scroll chat to bottom
     */
    private scrollToBottom(): void {
        const chatContainer = document.querySelector('.chat-messages');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    /**
     * Reconnect to WebSocket
     */
    reconnect(): void {
        const conversation = this.selectedConversation();
        if (conversation) {
            this.wsService.connect(conversation.id);
        }
    }
}
