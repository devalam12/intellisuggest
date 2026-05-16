import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomainOption, Domain } from '../../models/intellisuggest.models';

@Component({
  selector: 'app-domain-select',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './domain-select.component.html',
  styleUrls: ['./domain-select.component.scss'],
})
export class DomainSelectComponent {
  @Output() domainSelected = new EventEmitter<Domain>();

  domains: DomainOption[] = [
    { id: 'movies', label: 'Movies', icon: '🎬', desc: 'Find your next obsession' },
    { id: 'books', label: 'Books', icon: '📖', desc: 'Your next great read' },
    { id: 'careers', label: 'Careers', icon: '🚀', desc: 'Paths that fit who you are' },
    { id: 'restaurants', label: 'Restaurants', icon: '🍽️', desc: 'Dining tailored to your taste' },
  ];

  select(domain: Domain) {
    this.domainSelected.emit(domain);
  }
}
