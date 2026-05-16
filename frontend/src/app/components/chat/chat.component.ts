import {
  Component, Input, Output, EventEmitter,
  OnInit, ViewChild, ElementRef, AfterViewChecked, NgZone
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatMessage, Domain, UserPreferences } from '../../models/intellisuggest.models';
import { IntelliSuggestService } from '../../services/intellisuggest.service';

const OPENERS: Record<Domain, string> = {
  movies: "Hi! I'm here to find your perfect movie. Tell me about a film you absolutely loved — what made it special to you?",
  books: "Let's find your next great read! Tell me about a book you couldn't put down, or one that genuinely changed how you think.",
  careers: "Let's find career paths that fit who you are. What kind of work makes you feel most alive — even if it's just tasks or moments?",
  restaurants: "Let's find your ideal restaurant. Tell me about a meal that was genuinely memorable — what made it so good?",
};

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @Input() domain!: Domain;
  @Output() preferencesReady = new EventEmitter<UserPreferences>();
  @ViewChild('messagesEnd') messagesEnd!: ElementRef;
  @ViewChild('chatInput') chatInput!: ElementRef;

  messages: ChatMessage[] = [];
  inputText = '';
  isStreaming = false;
  streamingText = '';
  private shouldScroll = false;

  constructor(private service: IntelliSuggestService, private zone: NgZone) {}

  ngOnInit() {
    this.messages = [{ role: 'assistant', content: OPENERS[this.domain] }];
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.messagesEnd?.nativeElement?.scrollIntoView({ behavior: 'smooth' });
      this.shouldScroll = false;
    }
  }

  get displayStreamText(): string {
    return this.cleanText(this.streamingText);
  }

  private extractPreferences(text: string): UserPreferences | null {
    const match = text.match(/<preferences_ready>([\s\S]*?)<\/preferences_ready>/);
    if (match) {
      try { return JSON.parse(match[1].trim()); } catch { return null; }
    }
    return null;
  }

  private cleanText(text: string): string {
    return text.replace(/<preferences_ready>[\s\S]*?<\/preferences_ready>/g, '').trim();
  }

  handleKey(event: KeyboardEvent) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  }

  async send() {
    if (!this.inputText.trim() || this.isStreaming) return;

    const userMsg: ChatMessage = { role: 'user', content: this.inputText.trim() };
    this.messages = [...this.messages, userMsg];
    this.inputText = '';
    this.isStreaming = true;
    this.streamingText = '';
    this.shouldScroll = true;

    try {
      const fullText = await this.service.streamChat(
        this.messages,
        this.domain,
        (partial) => {
          this.zone.run(() => {
            this.streamingText = partial;
            this.shouldScroll = true;
          });
        }
      );

      const prefs = this.extractPreferences(fullText);
      const display = this.cleanText(fullText);

      this.zone.run(() => {
        this.messages = [...this.messages, { role: 'assistant', content: display }];
        this.streamingText = '';
        this.isStreaming = false;
        this.shouldScroll = true;
      });

      if (prefs) {
        setTimeout(() => this.zone.run(() => this.preferencesReady.emit(prefs)), 800);
      }
    } catch {
      this.zone.run(() => {
        this.messages = [...this.messages, {
          role: 'assistant',
          content: 'Something went wrong. Please try again.',
        }];
        this.isStreaming = false;
      });
    }
  }
}
