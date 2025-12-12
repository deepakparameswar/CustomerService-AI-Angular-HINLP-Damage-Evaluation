import { Component, OnInit, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { Issue } from '../../models/issue.model';
import { IssueService } from '../../services/issue.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="dashboard">
      <div class="container">
        <div class="table-container">
          <div class="table-wrapper">
            <table class="issues-table">
              <thead>
                <tr>
                  <th>Party Number</th>
                  <th>Party Name</th>
                  <th>Issue Description</th>
                  <th>Issue Title</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <ng-container *ngFor="let issue of issues">
                  <tr>
                    <td>{{ issue.userID }}</td>
                    <td>{{ issue.userName }}</td>
                    <td>{{ issue.issueDescription }}</td>
                    <td>{{ issue.issueTitle }}</td>
                    <td>
                      <button class="action-btn view-btn" (click)="viewIssue(issue)">View</button>
                      <button class="action-btn edit-btn" (click)="resolveIssue(issue)" [disabled]="isResolving(issue.userID)">
                        <span *ngIf="!isResolving(issue.userID)">Resolve</span>
                        <span *ngIf="isResolving(issue.userID)">⏳ Loading...</span>
                      </button>
                      <button *ngIf="issue.imageURL" class="action-btn expand-btn" (click)="toggleExpand(issue.userID)">
                        {{ isExpanded(issue.userID) ? '▼' : '▶' }}
                      </button>
                    </td>
                  </tr>
                  <tr *ngIf="issue.imageURL && isExpanded(issue.userID)" class="expanded-row">
                    <td colspan="5" class="image-cell">
                      <div class="image-container">
                        <img [src]="issue.imageURL" alt="Issue Image" class="issue-image" />
                        <button class="view-image-btn" (click)="viewImagePopup(issue.imageURL)">🔍 View</button>
                      </div>
                    </td>
                  </tr>
                </ng-container>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <div class="modal-overlay" *ngIf="selectedIssue" (click)="closeModal()">
      <div class="modal-content" (click)="$event.stopPropagation()">
        <div class="modal-header">
          <h2>Issue Details</h2>
          <button class="close-btn" (click)="closeModal()">&times;</button>
        </div>
        <div class="modal-body">
          <div class="detail-row">
            <label>User ID:</label>
            <span>{{ selectedIssue.userID }}</span>
          </div>
          <div class="detail-row">
            <label>User Name:</label>
            <span>{{ selectedIssue.userName }}</span>
          </div>
          <div class="detail-row">
            <label>Issue Title:</label>
            <span>{{ selectedIssue.issueTitle }}</span>
          </div>
          <div class="detail-row">
            <label>Issue Description:</label>
            <span>{{ selectedIssue.issueDescription }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="image-popup-overlay" *ngIf="popupImageUrl" (click)="closeImagePopup()">
      <div class="image-popup-content" (click)="$event.stopPropagation()">
        <button class="popup-close-btn" (click)="closeImagePopup()">&times;</button>
        <img [src]="popupImageUrl" alt="Issue Image" class="popup-image" />
      </div>
    </div>
  `,
  styles: [`
    .dashboard {
      height: 100%;
      display: flex;
      flex-direction: column;
      padding: 2rem 0;
      width: 100%;
    }
    
    .table-container {
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      width: 100%;
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    
    .issues-table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }
    
    .table-wrapper {
      flex: 1;
      overflow-y: auto;
      max-height: calc(100vh - 200px);
    }
    
    .issues-table thead {
      position: sticky;
      top: 0;
      z-index: 10;
    }
    
    .issues-table th {
      background: #f8f9fa;
      padding: 1rem;
      text-align: left;
      font-weight: 600;
      color: #333;
      border-bottom: 2px solid #dee2e6;
    }
    
    .issues-table th:nth-child(1) { width: 10%; }
    .issues-table th:nth-child(2) { width: 15%; }
    .issues-table th:nth-child(3) { width: 40%; }
    .issues-table th:nth-child(4) { width: 20%; }
    .issues-table th:nth-child(5) { width: 15%; }
    
    .issues-table td {
      padding: 1rem;
      border-bottom: 1px solid #dee2e6;
      color: #555;
    }
    
    .issues-table tr:hover {
      background: #f8f9fa;
    }
    
    .action-btn {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      margin-right: 0.5rem;
      font-size: 0.875rem;
      transition: background 0.2s;
    }
    
    .view-btn {
      background: #007bff;
      color: white;
    }
    
    .view-btn:hover {
      background: #0056b3;
    }
    
    .edit-btn {
      background: #28a745;
      color: white;
    }
    
    .edit-btn:hover {
      background: #1e7e34;
    }
    
    .edit-btn:disabled {
      background: #6c757d;
      cursor: not-allowed;
      opacity: 0.6;
    }
    
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    
    .modal-content {
      background: white;
      border-radius: 8px;
      width: 90%;
      max-width: 500px;
      max-height: 80vh;
      overflow-y: auto;
    }
    
    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem;
      border-bottom: 1px solid #dee2e6;
    }
    
    .modal-header h2 {
      margin: 0;
      color: #333;
    }
    
    .close-btn {
      background: none;
      border: none;
      font-size: 1.5rem;
      cursor: pointer;
      color: #666;
    }
    
    .close-btn:hover {
      color: #333;
    }
    
    .modal-body {
      padding: 1.5rem;
    }
    
    .detail-row {
      display: flex;
      margin-bottom: 1rem;
    }
    
    .detail-row label {
      font-weight: 600;
      width: 140px;
      color: #333;
    }
    
    .detail-row span {
      flex: 1;
      color: #555;
    }
    
    .expand-btn {
      background: #6c757d;
      color: white;
      padding: 0.3rem 0.6rem;
      margin-right: 0.5rem;
    }
    
    .expand-btn:hover {
      background: #545b62;
    }
    
    .expanded-row {
      background: #f8f9fa;
    }
    
    .image-cell {
      padding: 1rem;
      text-align: center;
    }
    
    .image-container {
      position: relative;
      display: inline-block;
    }
    
    .issue-image {
      max-width: 300px;
      max-height: 200px;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .view-image-btn {
      position: absolute;
      top: 10px;
      right: 10px;
      background: #ff6b35;
      color: white;
      border: 2px solid white;
      padding: 0.5rem 0.8rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: bold;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .view-image-btn:hover {
      background: #e55a2b;
      transform: scale(1.05);
      box-shadow: 0 3px 12px rgba(0,0,0,0.4);
    }
    
    .image-popup-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.8);
      backdrop-filter: blur(5px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 2000;
    }
    
    .image-popup-content {
      position: relative;
      max-width: 90vw;
      max-height: 90vh;
    }
    
    .popup-image {
      max-width: 100%;
      max-height: 100%;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .popup-close-btn {
      position: absolute;
      top: -40px;
      right: 0;
      background: rgba(255,255,255,0.9);
      border: none;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      font-size: 1.2rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .popup-close-btn:hover {
      background: white;
    }
  `]
})
export class DashboardComponent implements OnInit {
  issues: Issue[] = [];
  selectedIssue: Issue | null = null;
  expandedRows: Set<string> = new Set();
  popupImageUrl: string | null = null;
  resolvingIssues: Set<string> = new Set();

  constructor(private issueService: IssueService, private router: Router, private http: HttpClient) {}

  ngOnInit(): void {
    this.issueService.getIssues().subscribe({
      next: (data) => this.issues = data,
      error: (error) => console.error('Error fetching issues:', error)
    });
  }

  viewIssue(issue: Issue): void {
    this.selectedIssue = issue;
  }

  closeModal(): void {
    this.selectedIssue = null;
  }

  resolveIssue(issue: Issue): void {
    this.resolvingIssues.add(issue.userID);
    this.http.post('http://localhost:8000/start-execution', {
      issueDescription: issue.issueDescription
    }).subscribe({
      next: (response) => {
        this.resolvingIssues.delete(issue.userID);
        this.router.navigate(['/resolve'], {
          queryParams: {
            userID: issue.userID,
            userName: issue.userName,
            issueTitle: issue.issueTitle,
            issueDescription: issue.issueDescription,
            response: JSON.stringify(response),
            threadID: issue.threadID,
            imageURL: issue?.imageURL
          }
        });
      },
      error: (error) => {
        this.resolvingIssues.delete(issue.userID);
        console.error('API Error:', error);
      }
    });
  }

  isResolving(userID: string): boolean {
    return this.resolvingIssues.has(userID);
  }

  toggleExpand(userID: string): void {
    if (this.expandedRows.has(userID)) {
      this.expandedRows.delete(userID);
    } else {
      this.expandedRows.add(userID);
    }
  }

  isExpanded(userID: string): boolean {
    return this.expandedRows.has(userID);
  }

  viewImagePopup(imageUrl: string): void {
    this.popupImageUrl = imageUrl;
  }

  closeImagePopup(): void {
    this.popupImageUrl = null;
  }

  @HostListener('document:keydown.escape', ['$event'])
  onEscapeKey(event: KeyboardEvent): void {
    if (this.popupImageUrl) {
      this.closeImagePopup();
    } else {
      this.closeModal();
    }
  }
}