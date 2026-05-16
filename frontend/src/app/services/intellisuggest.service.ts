import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ChatMessage, UserPreferences, RecommendationResponse, Domain } from '../models/intellisuggest.models';

@Injectable({ providedIn: 'root' })
export class IntelliSuggestService {
  private baseUrl = 'https://intellisuggest-api.onrender.com';

  constructor(private http: HttpClient) {}

  getDomains(): Observable<{ domains: string[] }> {
    return this.http.get<{ domains: string[] }>(`${this.baseUrl}/domains`);
  }

  getRecommendations(
    preferences: UserPreferences,
    domain: Domain,
    feedback?: string
  ): Observable<RecommendationResponse> {
    return this.http.post<RecommendationResponse>(`${this.baseUrl}/recommend`, {
      preferences,
      domain,
      feedback: feedback ?? null,
    });
  }

  async streamChat(
  messages: ChatMessage[],
  domain: Domain,
  onChunk: (text: string) => void
): Promise<string> {
  const response = await fetch(`${this.baseUrl}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages, domain }),
  });
  const data = await response.json();
  onChunk(data.text);
  return data.text;
}

  // async streamChat(
  //   messages: ChatMessage[],
  //   domain: Domain,
  //   onChunk: (text: string) => void
  // ): Promise<string> {
  //   const response = await fetch(`${this.baseUrl}/chat`, {
  //     method: 'POST',
  //     headers: { 'Content-Type': 'application/json' },
  //     body: JSON.stringify({ messages, domain }),
  //   });

  //   const reader = response.body!.getReader();
  //   const decoder = new TextDecoder();
  //   let fullText = '';

  //   while (true) {
  //     const { done, value } = await reader.read();
  //     if (done) break;
  //     const chunk = decoder.decode(value);
  //     for (const line of chunk.split('\n')) {
  //       if (line.startsWith('data: ') && line !== 'data: [DONE]') {
  //         try {
  //           const parsed = JSON.parse(line.slice(6));
  //           fullText += parsed.text;
  //           onChunk(fullText);
  //         } catch {}
  //       }
  //     }
  //   }
  //   return fullText;
  // }
}
