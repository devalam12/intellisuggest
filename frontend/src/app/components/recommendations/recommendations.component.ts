import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Recommendation, RecommendationResponse, UserPreferences, Domain } from '../../models/intellisuggest.models';
import { IntelliSuggestService } from '../../services/intellisuggest.service';

@Component({
  selector: 'app-recommendations',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './recommendations.component.html',
  styleUrls: ['./recommendations.component.scss'],
})
export class RecommendationsComponent implements OnChanges {
  @Input() recommendations: RecommendationResponse | null = null;
  @Input() preferences!: UserPreferences;
  @Input() domain!: Domain;
  @Input() isLoading = false;
  @Output() refine = new EventEmitter<string>();

  feedbackText = '';
  isRefining = false;
  expandedIndex: number | null = null;

  ngOnChanges() {
    this.isRefining = false;
  }

  toggleExpand(i: number) {
    this.expandedIndex = this.expandedIndex === i ? null : i;
  }

  matchLabel(score: number): { text: string; cls: string } {
    if (score >= 0.9) return { text: 'Perfect match', cls: 'label-green' };
    if (score >= 0.75) return { text: 'Strong match', cls: 'label-blue' };
    if (score >= 0.6) return { text: 'Good match', cls: 'label-amber' };
    return { text: 'Worth trying', cls: 'label-gray' };
  }

  scorePct(score: number): number {
    return Math.round(score * 100);
  }

  async submitRefine() {
    if (!this.feedbackText.trim()) return;
    this.isRefining = true;
    this.refine.emit(this.feedbackText);
    this.feedbackText = '';
  }

  handleRefineKey(e: KeyboardEvent) {
    if (e.key === 'Enter') this.submitRefine();
  }
}
