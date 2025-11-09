import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './components/header/header.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, HeaderComponent],
  template: `
    <div class="app">
      <app-header></app-header>
      <main class="main-content">
        <router-outlet></router-outlet>
      </main>
    </div>
  `,
  styles: [`
    .app {
      height: 100vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    
    .main-content {
      flex: 1;
      overflow: hidden;
    }
  `]
})
export class AppComponent {
  title = 'lic-customer-service';
}