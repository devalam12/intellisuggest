import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AppPhase, Domain, UserPreferences, RecommendationResponse } from './models/intellisuggest.models';
import { IntelliSuggestService } from './services/intellisuggest.service';
import { DomainSelectComponent } from './components/domain-select/domain-select.component';
import { ChatComponent } from './components/chat/chat.component';
import { RecommendationsComponent } from './components/recommendations/recommendations.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, DomainSelectComponent, ChatComponent, RecommendationsComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  phase: AppPhase = 'select';
  domain: Domain | null = null;
  preferences: UserPreferences | null = null;
  recommendations: RecommendationResponse | null = null;
  isLoadingRecs = false;

  constructor(private service: IntelliSuggestService) {}

  onDomainSelected(domain: Domain) {
    this.domain = domain;
    this.phase = 'chat';
  }

  onPreferencesReady(prefs: UserPreferences) {
    this.preferences = prefs;
    this.phase = 'results';
    this.isLoadingRecs = true;
    this.service.getRecommendations(prefs, this.domain!).subscribe({
      next: (data) => { this.recommendations = data; this.isLoadingRecs = false; },
      error: () => { this.isLoadingRecs = false; },
    });
  }

  onRefine(feedback: string) {
    this.isLoadingRecs = true;
    this.service.getRecommendations(this.preferences!, this.domain!, feedback).subscribe({
      next: (data) => { this.recommendations = data; this.isLoadingRecs = false; },
      error: () => { this.isLoadingRecs = false; },
    });
  }

  reset() {
    this.phase = 'select';
    this.domain = null;
    this.preferences = null;
    this.recommendations = null;
  }
}
