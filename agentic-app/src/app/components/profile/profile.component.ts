import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="profile-page">
      <div class="container">
        <div class="profile-header">
          <h2>User Profile</h2>
          <button class="back-btn" (click)="goBack()">← Back to Dashboard</button>
        </div>
        
        <div class="profile-content">
          <div class="profile-card">
            <div class="profile-avatar">
              <div class="avatar-circle">
                <span>JD</span>
              </div>
            </div>
            
            <div class="profile-info">
              <div class="info-section">
                <h3>Personal Information</h3>
                <div class="info-grid">
                  <div class="info-item">
                    <label>Full Name</label>
                    <span>John Doe</span>
                  </div>
                  <div class="info-item">
                    <label>Employee ID</label>
                    <span>EMP001</span>
                  </div>
                  <div class="info-item">
                    <label>Email</label>
                    <span>john.doe&#64;lic.com</span>
                  </div>
                  <div class="info-item">
                    <label>Department</label>
                    <span>Customer Service</span>
                  </div>
                  <div class="info-item">
                    <label>Role</label>
                    <span>Senior Agent</span>
                  </div>
                  <div class="info-item">
                    <label>Phone</label>
                    <span>+91 98765 43210</span>
                  </div>
                </div>
              </div>
              
              <div class="info-section">
                <h3>Account Settings</h3>
                <div class="settings-actions">
                  <button class="settings-btn">Change Password</button>
                  <button class="settings-btn">Update Profile</button>
                  <button class="settings-btn">Notification Settings</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .profile-page {
      height: 100%;
      padding: 2rem 0;
    }
    
    .profile-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
    }
    
    .profile-header h2 {
      color: #333;
      margin: 0;
    }
    
    .back-btn {
      padding: 0.5rem 1rem;
      background: #6c757d;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      text-decoration: none;
    }
    
    .back-btn:hover {
      background: #545b62;
    }
    
    .profile-card {
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      padding: 2rem;
      display: flex;
      gap: 2rem;
    }
    
    .profile-avatar {
      flex: 0 0 150px;
      text-align: center;
    }
    
    .avatar-circle {
      width: 120px;
      height: 120px;
      background: #007bff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 2rem;
      font-weight: bold;
      margin: 0 auto;
    }
    
    .profile-info {
      flex: 1;
    }
    
    .info-section {
      margin-bottom: 2rem;
    }
    
    .info-section h3 {
      color: #333;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid #007bff;
    }
    
    .info-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 1rem;
    }
    
    .info-item {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }
    
    .info-item label {
      font-weight: 600;
      color: #666;
      font-size: 0.875rem;
    }
    
    .info-item span {
      color: #333;
      font-size: 1rem;
    }
    
    .settings-actions {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }
    
    .settings-btn {
      padding: 0.75rem 1.5rem;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.875rem;
      transition: background 0.2s;
    }
    
    .settings-btn:hover {
      background: #0056b3;
    }
  `]
})
export class ProfileComponent {
  constructor(private router: Router) {}

  goBack(): void {
    this.router.navigate(['/dashboard']);
  }
}