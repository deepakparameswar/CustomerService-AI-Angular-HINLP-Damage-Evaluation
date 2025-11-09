import { Component, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  template: `
    <header class="header">
      <div class="container">
        <div class="header-content">
          <h1 class="app-name" (click)="goHome()">LIC Customer Service</h1>
          <div class="user-profile" (click)="toggleDropdown()" #userProfile>
            <div class="profile-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 1L9 7V9C9 10.1 9.9 11 11 11V16L7.5 17.5C7.09 17.66 6.84 18.08 6.84 18.54C6.84 19.17 7.33 19.66 7.96 19.66H16.04C16.67 19.66 17.16 19.17 17.16 18.54C17.16 18.08 16.91 17.66 16.5 17.5L13 16V11C14.1 11 15 10.1 15 9Z"/>
              </svg>
              <span class="username">John Doe</span>
              <svg class="dropdown-arrow" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7 10l5 5 5-5z"/>
              </svg>
            </div>
            <div class="dropdown-menu" [class.show]="isDropdownOpen">
              <a (click)="goToProfile()" class="dropdown-item">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
                Profile
              </a>
              <a (click)="logout()" class="dropdown-item logout">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.59L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
                </svg>
                Logout
              </a>
            </div>
          </div>
        </div>
      </div>
    </header>
  `,
  styles: [`
    .header {
      background: #fff;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      position: sticky;
      top: 0;
      z-index: 100;
    }
    
    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem 0;
    }
    
    .app-name {
      color: #333;
      font-size: 1.5rem;
      font-weight: 600;
      cursor: pointer;
    }
    
    .user-profile {
      position: relative;
    }
    
    .profile-icon {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: #f8f9fa;
      border: 1px solid #dee2e6;
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
      color: #495057;
    }
    
    .profile-icon:hover {
      background: #e9ecef;
      border-color: #adb5bd;
    }
    
    .username {
      font-size: 0.875rem;
      font-weight: 500;
    }
    
    .dropdown-arrow {
      transition: transform 0.2s;
    }
    
    .profile-icon:hover .dropdown-arrow {
      transform: rotate(180deg);
    }
    
    .dropdown-menu {
      position: absolute;
      top: 100%;
      right: 0;
      background: white;
      border: 1px solid #dee2e6;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      min-width: 160px;
      opacity: 0;
      visibility: hidden;
      transform: translateY(-10px);
      transition: all 0.2s;
      z-index: 1000;
      margin-top: 4px;
    }
    
    .dropdown-menu.show {
      opacity: 1;
      visibility: visible;
      transform: translateY(0);
    }
    
    .dropdown-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      text-decoration: none;
      color: #495057;
      font-size: 0.875rem;
      transition: background 0.2s;
    }
    
    .dropdown-item:hover {
      background: #f8f9fa;
      color: #007bff;
    }
    
    .dropdown-item.logout:hover {
      background: #fff5f5;
      color: #dc3545;
    }
  `]
})
export class HeaderComponent {
  isDropdownOpen = false;

  constructor(private router: Router) {}

  toggleDropdown(): void {
    this.isDropdownOpen = !this.isDropdownOpen;
  }

  goToProfile(): void {
    this.isDropdownOpen = false;
    this.router.navigate(['/profile']);
  }

  logout(): void {
    localStorage.removeItem('token');
    this.router.navigate(['/login']);
  }

  goHome(): void {
    this.router.navigate(['/dashboard']);
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: Event): void {
    const target = event.target as HTMLElement;
    const userProfile = document.querySelector('.user-profile');
    
    if (userProfile && !userProfile.contains(target)) {
      this.isDropdownOpen = false;
    }
  }
}