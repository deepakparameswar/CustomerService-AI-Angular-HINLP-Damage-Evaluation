import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="login-container">
      <div class="login-card">
        <h2>Login to LIC Customer Service</h2>
        <form (ngSubmit)="onLogin()" #loginForm="ngForm">
          <div class="form-group">
            <label for="username">Username</label>
            <input 
              type="text" 
              id="username" 
              name="username"
              [(ngModel)]="username" 
              required 
              placeholder="Enter username">
          </div>
          
          <div class="form-group">
            <label for="password">Password</label>
            <input 
              type="password" 
              id="password" 
              name="password"
              [(ngModel)]="password" 
              required 
              placeholder="Enter password">
          </div>
          
          <div class="error-message" *ngIf="errorMessage">
            {{ errorMessage }}
          </div>
          
          <button type="submit" class="login-btn" [disabled]="!loginForm.form.valid || isLoading">
            {{ isLoading ? 'Logging in...' : 'Login' }}
          </button>
        </form>
        
        <div class="demo-credentials">
          <p><strong>Demo Credentials:</strong></p>
          <p>Username: admin</p>
          <p>Password: password</p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .login-container {
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .login-card {
      background: white;
      padding: 2rem;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.2);
      width: 100%;
      max-width: 400px;
    }
    
    h2 {
      text-align: center;
      margin-bottom: 2rem;
      color: #333;
    }
    
    .form-group {
      margin-bottom: 1.5rem;
    }
    
    label {
      display: block;
      margin-bottom: 0.5rem;
      color: #555;
      font-weight: 500;
    }
    
    input {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 1rem;
      transition: border-color 0.2s;
    }
    
    input:focus {
      outline: none;
      border-color: #667eea;
    }
    
    .login-btn {
      width: 100%;
      padding: 0.75rem;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      cursor: pointer;
      transition: background 0.2s;
    }
    
    .login-btn:hover:not(:disabled) {
      background: #5a6fd8;
    }
    
    .login-btn:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
    
    .error-message {
      color: #dc3545;
      margin-bottom: 1rem;
      text-align: center;
      font-size: 0.875rem;
    }
    
    .demo-credentials {
      margin-top: 2rem;
      padding: 1rem;
      background: #f8f9fa;
      border-radius: 6px;
      font-size: 0.875rem;
    }
    
    .demo-credentials p {
      margin: 0.25rem 0;
    }
  `]
})
export class LoginComponent {
  username = '';
  password = '';
  errorMessage = '';
  isLoading = false;
  private apiUrl = 'http://localhost:8000';

  constructor(private router: Router, private http: HttpClient) {}

  onLogin(): void {
    this.isLoading = true;
    this.errorMessage = '';

    this.http.post<any>(`${this.apiUrl}/login`, {
      username: this.username,
      password: this.password
    }).subscribe({
      next: (response) => {
        if (response.success) {
          localStorage.setItem('token', response.token);
          this.router.navigate(['/dashboard']);
        }
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Invalid username or password';
        this.isLoading = false;
      }
    });
  }
}