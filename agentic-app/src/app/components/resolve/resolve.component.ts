import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router, ActivatedRoute } from '@angular/router';
import { Issue } from '../../models/issue.model';
import {TitleCaseFromUnderscorePipe} from '../../pipes/title-case-from-underscore.pipe'

@Component({
  selector: 'app-resolve',
  standalone: true,
  imports: [CommonModule, TitleCaseFromUnderscorePipe],
  template: `
    <div class="resolve-page">
      <div class="container">
        <div class="content-layout">
          <div class="left-section">
            <div class="card">
              <h3>Issue Details</h3>
              <div class="card-content">
                <p>User ID: {{ selectedIssue?.userID || 'N/A' }}</p>
                <p>User Name: {{ selectedIssue?.userName || 'N/A' }}</p>
                <p>Issue Title: {{ selectedIssue?.issueTitle || 'N/A' }}</p>
                <p>Issue Description: {{ selectedIssue?.issueDescription || 'N/A' }}</p>
                <p>Status: In Progress</p>
              </div>
            </div>
          </div>
          
          <div class="right-section">
            <div class="card">
              <h3>AI Agentic Workflow - SOP Execution</h3>
              <div class="card-content">
                <div class="start-section" *ngIf="!apiResponse">
                  <div class="start-layout">
                    <div class="sop-procedures">
                      <h4>SOP Procedures</h4>
                      <div class="procedure-description">
                        <p>{{response.response.generation}}</p>
                      </div>
                    </div>
                    <div class="start-controls">
                      <p class="workflow-description">Ready to execute Standard Operating Procedure for issue resolution.</p>
                      <button class="btn-start" (click)="startExecution()">▶ Start Execution</button>
                    </div>
                  </div>
                </div>
                
                <div class="execution-content" *ngIf="apiResponse">
                <div class="workflow-status">
                  <div class="status-badge executing"><span class="blinking-dot">●</span> Executing SOP</div>
                  <span class="workflow-id">Workflow ID: WF-2024-001</span>
                </div>
                
                <div class="sop-section">
                  <h4>Standard Operating Procedure</h4>
                  <div class="sop-steps">
                    <div class="sop-step {{getStatusLabel(entry.status)}}" *ngFor="let entry of getToolsDetails(); let i=index">
                      <div class="step-header">
                        <span class="step-number">{{i+1}}</span>
                        <span class="step-title">{{ entry.tool_name | titleCaseFromUnderscore }}</span>
                        <span class="step-status" *ngIf="entry.status=='pending_approval'">⏳ Pending Approval</span>
                        <span class="step-status" *ngIf="entry.status=='waiting'">⏸ Waiting</span>
                        <span class="step-status" *ngIf="entry.status=='completed'">✓ Completed</span>
                      </div>
                      <div class="step-details">Planning to call {{entry.tool_name | titleCaseFromUnderscore}} with arguments : {{entry.tool_arguments}}</div>
                      <div class="approval-actions" *ngIf="entry.status=='pending_approval'">
                        <button class="approve-btn" (click)="actionStep(entry, true)">✓ Approve</button>
                        <button class="reject-btn" (click)="actionStep(entry, false)">✗ Reject</button>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="agent-info">
                  <h4>Agent Execution Details</h4>
                  <div class="agent-details">
                    <p><strong>Assigned Agent:</strong> AI Agent Alpha-7</p>
                    <p><strong>Execution Time:</strong> 2 minutes 34 seconds</p>
                    <p><strong>Confidence Score:</strong> 94%</p>
                  </div>
                </div>
                
                <div class="admin-notes">
                  <h4>Admin Notes</h4>
                  <textarea placeholder="Add your approval notes or feedback..." rows="3"></textarea>
                </div>
                
                <div class="api-response" *ngIf="apiResponse">
                  <h4>SOP Execution Response</h4>
                  <div class="response-content">
                    <div class="response-text" *ngIf="apiResponse.response?.generation">
                      {{ apiResponse.response.generation }}
                    </div>
                    <div class="response-fallback" *ngIf="!apiResponse.response?.generation">
                      <pre>{{ apiResponse | json }}</pre>
                    </div>
                  </div>
                </div>
                
                <div class="workflow-actions">
                  <button class="btn-success">✓ Approve Entire Workflow</button>
                  <button class="btn-danger">✗ Reject Workflow</button>
                  <button class="btn-warning">⏸ Pause Execution</button>
                </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .resolve-page {
      height: 100%;
      padding: 2rem 0;
    }
    
    .content-layout {
      display: flex;
      gap: 2rem;
      height: 100%;
    }
    
    .left-section {
      flex: 0 0 16.667%;
    }
    
    .right-section {
      flex: 1;
    }
    
    .card {
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      height: 100%;
    }
    
    .card h3 {
      padding: 1.5rem;
      margin: 0;
      border-bottom: 1px solid #dee2e6;
      color: #333;
    }
    
    .card-content {
      padding: 1.5rem;
      max-height: calc(100vh - 200px);
      overflow-y: auto;
    }
    
    .card-content p {
      margin-bottom: 1rem;
      color: #555;
    }
    
    textarea {
      width: 100%;
      border: 1px solid #dee2e6;
      border-radius: 4px;
      padding: 1rem;
      font-family: inherit;
      resize: vertical;
      margin-bottom: 1rem;
    }
    
    .action-buttons {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }
    
    .btn-primary, .btn-secondary {
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.875rem;
      transition: background 0.2s;
    }
    
    .btn-primary {
      background: #28a745;
      color: white;
    }
    
    .btn-primary:hover {
      background: #1e7e34;
    }
    
    .btn-secondary {
      background: #6c757d;
      color: white;
    }
    
    .btn-secondary:hover {
      background: #545b62;
    }
    
    .workflow-status {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
      padding: 1rem;
      background: #f8f9fa;
      border-radius: 6px;
    }
    
    .status-badge {
      padding: 0.5rem 1rem;
      border-radius: 20px;
      font-size: 0.875rem;
      font-weight: 600;
    }
    
    .status-badge.executing {
      background: #fff3cd;
      color: #856404;
    }
    
    .blinking-dot {
      animation: colorBlink 1s infinite;
    }
    
    @keyframes colorBlink {
      0%, 50% { color: #dc3545; }
      51%, 100% { color: #28a745; }
    }
    
    .workflow-id {
      font-size: 0.875rem;
      color: #666;
    }
    
    .sop-section {
      margin-bottom: 2rem;
    }
    
    .sop-section h4 {
      color: #333;
      margin-bottom: 1rem;
      border-bottom: 2px solid #007bff;
      padding-bottom: 0.5rem;
    }
    
    .sop-steps {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    
    .sop-step {
      border: 1px solid #dee2e6;
      border-radius: 8px;
      padding: 1rem;
      transition: all 0.2s;
    }
    
    .sop-step.completed {
      border-color: #28a745;
      background: #f8fff9;
    }
    
    .sop-step.pending {
      border-color: #ffc107;
      background: #fffdf0;
    }
    
    .sop-step.waiting {
      border-color: #6c757d;
      background: #f8f9fa;
    }
    
    .step-header {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 0.5rem;
    }
    
    .step-number {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      background: #007bff;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 0.875rem;
    }
    
    .step-title {
      flex: 1;
      font-weight: 600;
      color: #333;
    }
    
    .step-status {
      font-size: 0.875rem;
      font-weight: 500;
    }
    
    .step-details {
      margin-left: 46px;
      color: #666;
      font-size: 0.875rem;
      margin-bottom: 0.5rem;
    }
    
    .approval-actions {
      margin-left: 46px;
      display: flex;
      gap: 0.5rem;
    }
    
    .approve-btn, .reject-btn {
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 4px;
      font-size: 0.875rem;
      cursor: pointer;
      transition: background 0.2s;
    }
    
    .approve-btn {
      background: #28a745;
      color: white;
    }
    
    .approve-btn:hover {
      background: #1e7e34;
    }
    
    .reject-btn {
      background: #dc3545;
      color: white;
    }
    
    .reject-btn:hover {
      background: #c82333;
    }
    
    .agent-info, .admin-notes {
      margin-bottom: 1.5rem;
    }
    
    .agent-info h4, .admin-notes h4 {
      color: #333;
      margin-bottom: 0.75rem;
      font-size: 1rem;
    }
    
    .agent-details p {
      margin: 0.25rem 0;
      font-size: 0.875rem;
      color: #555;
    }
    
    .admin-notes textarea {
      width: 100%;
      border: 1px solid #dee2e6;
      border-radius: 4px;
      padding: 0.75rem;
      font-family: inherit;
      resize: vertical;
    }
    
    .workflow-actions {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }
    
    .btn-success, .btn-danger, .btn-warning {
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.875rem;
      font-weight: 500;
      transition: background 0.2s;
    }
    
    .btn-success {
      background: #28a745;
      color: white;
    }
    
    .btn-success:hover {
      background: #1e7e34;
    }
    
    .btn-danger {
      background: #dc3545;
      color: white;
    }
    
    .btn-danger:hover {
      background: #c82333;
    }
    
    .btn-warning {
      background: #ffc107;
      color: #212529;
    }
    
    .btn-warning:hover {
      background: #e0a800;
    }
    
    .start-section {
      padding: 2rem;
    }
    
    .start-layout {
      display: flex;
      gap: 2rem;
      align-items: center;
      justify-content: center;
    }
    
    .sop-procedures {
      flex: 1;
      background: #f8f9fa;
      padding: 1.5rem;
      border-radius: 8px;
      border: 1px solid #dee2e6;
    }
    
    .sop-procedures h4 {
      margin: 0 0 1rem 0;
      color: #333;
      font-size: 1.1rem;
      border-bottom: 2px solid #007bff;
      padding-bottom: 0.5rem;
    }
    
    .procedure-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
    
    .procedure-item {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.5rem;
      background: white;
      border-radius: 6px;
      border: 1px solid #e9ecef;
    }
    
    .procedure-number {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #007bff;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 0.75rem;
    }
    
    .procedure-description {
      line-height: 1.6;
    }
    
    .procedure-description p {
      margin-bottom: 1rem;
      color: #555;
      font-size: 0.875rem;
    }
    
    .procedure-description code {
      background: #e9ecef;
      padding: 0.2rem 0.4rem;
      border-radius: 3px;
      font-family: 'Courier New', monospace;
      font-size: 0.8rem;
      color: #495057;
    }
    
    .start-controls {
      flex: 1;
      text-align: center;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
    
    .workflow-description {
      font-size: 1rem;
      color: #666;
      margin-bottom: 1.5rem;
    }
    
    .btn-start {
      padding: 1rem 2rem;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      box-shadow: 0 2px 4px rgba(0,123,255,0.2);
    }
    
    .btn-start:hover {
      background: #0056b3;
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(0,123,255,0.3);
    }
    
    .execution-content {
      animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
    
    .api-response {
      margin-bottom: 1.5rem;
      padding: 1rem;
      background: #f8f9fa;
      border-radius: 6px;
      border: 1px solid #dee2e6;
    }
    
    .api-response h4 {
      color: #333;
      margin-bottom: 0.75rem;
      font-size: 1rem;
    }
    
    .response-content pre {
      background: white;
      padding: 1rem;
      border-radius: 4px;
      border: 1px solid #dee2e6;
      font-size: 0.875rem;
      overflow-x: auto;
      margin: 0;
    }
  `]
})
export class ResolveComponent implements OnInit {
  selectedIssue: Issue | null = null;
  apiResponse: any = null;
  response: any = null;
  sopMap:Map<string, [any]> = new Map<string, [any]>();

  constructor(private http: HttpClient, private router: Router, private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      if (params['userID']) {
        this.selectedIssue = {
          userID: params['userID'],
          userName: params['userName'],
          issueTitle: params['issueTitle'],
          issueDescription: params['issueDescription'],
          threadID: params['threadID']
        };
        if (params['response']) {
          this.response = JSON.parse(params['response']);
          console.log('Parsed response:', this.response);
        }
      }
    });
  }

  startExecution(): void {
    if (!this.selectedIssue) {
      console.error('No issue selected');
      return;
    }

    let threadID = this.selectedIssue.threadID;
    
    this.http.post('http://localhost:8000/process-sopquery', {
      operating_procedure: this.response.response.generation,
      userID: this.selectedIssue.userID,
      threadID: threadID
    }).subscribe({
      next: (response: any) => {
        console.log('API Response:', response);
        this.apiResponse = response.response;
        this.apiResponse["status"] = "pending_approval";
        this.sopMap.set(threadID, [this.apiResponse]);
        console.log('SOP Map:', this.sopMap);
      },
      error: (error) => {
        console.error('API Error:', error);
      }
    });
  }

  actionStep(entry:any, action: boolean): void {
    if (!this.selectedIssue) {
      console.error('No issue selected');
      return;
    }

    let threadID = this.selectedIssue.threadID;

    let executionObjs = this.sopMap.get(threadID);

    console.log(`executionObjs: ${executionObjs}`)

    console.log(`action ${action}`);
    console.log(`executionId ${threadID}`);
    console.log(`entry: ${entry}`)

    if(entry) {
      entry.status = 'waiting';
    }
    let body = {
      threadID: threadID,
      approved: action
    }
    this.http.post('http://localhost:8000/executions/approve', body).subscribe({
      next: (response: any) => {
        console.log('API Response:', response);
        this.apiResponse = response;
        this.apiResponse["status"] = "pending_approval";
        this.apiResponse["requires_approval"] = true;
        executionObjs?.push(this.apiResponse)
        entry.status = 'completed';
        console.log('SOP Map After Approval:', this.sopMap);
      },
      error: (error) => {
        console.error('API Error:', error);
      }
    });
  }

  getPendingActions():void {
    this.http.get('http://localhost:8000/executions/pending').subscribe({
      next: (response: any) => {
        console.log('API Response:', response);
        
      },
      error: (error) => {
        console.error('API Error:', error);
      }
    });
  }

  getStatusLabel(status: string): string {
    console.log("getStatusLabel status: >>>>> ",status)
    switch (status) {
      case 'completed': return 'completed';
      case 'pending_approval': return 'pending';
      default: return 'waiting';
    }
  }

  getToolsDetails() {
    let items;
    if(this.selectedIssue && this.selectedIssue.threadID) {
      items = this.sopMap.get(this.selectedIssue.threadID)
      console.log("getToolsDetails items >>>>>> ",items)
    }
    return items;
  }

}