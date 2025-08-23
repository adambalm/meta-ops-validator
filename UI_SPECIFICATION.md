# MetaOps Validator MVP - UI Specification

## Executive Summary

This specification defines the user interface for MetaOps Validator MVP, targeting mid-tier publishers who currently spend 30-60 minutes per title on manual ONIX validation. The goal is to reduce this to under 5 minutes through intelligent automation and clear, actionable feedback.

**Design Philosophy**: Business tool aesthetic - professional, data-dense, actionable. Following Tufte principles: maximize data-ink ratio, eliminate chartjunk, prioritize clarity over decoration.

---

## 1. User Flow Overview

### Primary User Journey: Validation Workflow
```
File Upload → Processing Status → Results Dashboard → Error Resolution → Export/Continue
```

### Key User Personas
- **Production Manager**: Needs overview of batch operations, error trends, team productivity
- **Metadata Editor**: Needs detailed error guidance, field-level validation, quick fixes
- **Technical Staff**: Needs raw validation output, API integration status, system health

### Critical Success Metrics
- Time to first validation result: <30 seconds
- Time to understand critical errors: <60 seconds  
- Time to complete error resolution: <3 minutes
- Overall workflow completion: <5 minutes

---

## 2. Screen-by-Screen Specifications

### 2.1 Upload Screen (`/upload`)

**Layout**: Single-column centered layout, 800px max width

**Components**:
```
[Header: MetaOps Validator]
[Breadcrumb: Upload]

[File Drop Zone]
- Drag & drop area (400x200px)
- "Choose File" button
- Accepted formats: .xml, .zip
- Max file size: 50MB
- Visual feedback on hover/drag

[Upload Options Panel]
┌─ Validation Level ─┐
│ ○ Quick (XSD only) │
│ ● Standard (XSD + Rules) │
│ ○ Complete (XSD + Rules + Schematron) │
└────────────────────┘

[Previous Uploads Table]
- Last 10 files
- Columns: Filename, Date, Status, Nielsen Score, Actions
- Status icons: ✓ (success), ⚠ (warnings), ✗ (errors), ⏳ (processing)

[Upload Button] - Primary CTA, disabled until file selected
```

**Interactions**:
- Drag/drop: Highlight border, show file preview
- File validation: Real-time format checking
- Upload progress: Linear progress bar with percentage
- Error states: Clear messaging with retry option

### 2.2 Processing Status Screen (`/processing/:jobId`)

**Layout**: Full-width with centered content

**Components**:
```
[Header with Job ID and timestamp]

[Progress Indicators]
┌─ XSD Validation ────────────┐
│ ✓ Namespace check          │
│ ✓ Schema structure         │
│ ⏳ Element validation      │
│ ⏸ Content rules            │
└───────────────────────────┘

[Real-time Log Stream]
- Scrollable area (600px height)
- Syntax highlighted
- Auto-scroll to bottom
- Collapsible sections by validation type

[Quick Stats Panel]
- Elements processed: 1,247 / 3,891
- Errors found: 12
- Warnings: 3
- Estimated completion: 2m 15s
```

**Interactions**:
- Auto-refresh every 2 seconds
- "View Details" expands log sections
- "Cancel Job" with confirmation dialog
- Automatic redirect to results on completion

### 2.3 Results Dashboard (`/results/:jobId`)

**Layout**: Three-column layout (sidebar + main + details)

#### Left Sidebar (300px):
```
[Nielsen Score Card]
┌─ ONIX Completeness ─┐
│      87%            │
│   ████████░░        │
│                     │
│ Required: 94%       │
│ Optional: 73%       │
│ Recommended: 89%    │
└─────────────────────┘

[Validation Summary]
- Status: ⚠ Needs Review
- Total Issues: 15
- Critical: 3
- Warnings: 12
- Processing time: 45s

[Filter & Actions]
□ Show only critical
□ Show recommendations  
[Export Report] [Re-validate]
```

#### Main Content Area:
```
[Tabbed Interface]
Tab 1: Issues (default)
Tab 2: Recommendations  
Tab 3: Raw Output

[Issues List - Grouped by Severity]
┌─ CRITICAL ERRORS (3) ─┐
│ 📍 Missing Required ISBN    │
│ 📍 Invalid Price Currency   │
│ 📍 Malformed Contributor   │
└─────────────────────────────┘

┌─ WARNINGS (12) ──────────┐
│ ⚠ Recommended field missing │
│ ⚠ Date format inconsistent │
│ [Show 10 more...]          │
└───────────────────────────┘

[Issue Detail Card Template]
┌─────────────────────────────────────┐
│ 📍 Missing Required ISBN             │
│                                     │
│ Element: Product > Identifier       │
│ Line: 247                          │
│ XPath: //Product[1]/Identifier[1]   │
│                                     │
│ Problem: ISBN identifier required   │
│ for trade books                     │
│                                     │
│ Fix: Add <Identifier> element with  │
│ IdentifierType=15 and valid ISBN    │
│                                     │
│ Example:                            │
│ <Identifier>                        │
│   <IdentifierType>15</IdentifierType>│
│   <IDValue>9781234567890</IDValue>   │
│ </Identifier>                       │
│                                     │
│ [View Context] [Mark as Resolved]    │
└─────────────────────────────────────┘
```

#### Right Details Panel (400px):
```
[Context Viewer]
- XML snippet with line numbers
- Syntax highlighting  
- Error location highlighted
- Collapsible parent elements

[Recommendations Engine]
- AI-suggested fixes
- Similar successful examples
- Industry best practices
```

**Interactions**:
- Click issue → expand detail card
- Hover issue → preview in sidebar
- Filter controls update URL state
- Export generates PDF/Excel report
- Real-time validation status updates

### 2.4 Batch Processing Dashboard (`/batch`)

**Layout**: Full-width dashboard layout

**Components**:
```
[KPI Header Strip]
Files Today: 127 | Avg Nielsen: 89% | Issues Resolved: 94% | Time Saved: 47h

[Processing Queue]
┌─ Active Jobs (3) ─────────────────────────┐
│ novel_spring2024.xml    ████████░░ 80%    │
│ cookbook_series.xml     ██░░░░░░░░ 20%    │  
│ textbook_math.xml       ████████░░ 85%    │
└─────────────────────────────────────────────┘

[Recent Completions Table]
Columns: Filename | Completed | Nielsen Score | Issues | Time Taken | Actions
- Sortable columns
- Status color coding
- Action buttons: View, Re-process, Download

[Analytics Charts]
┌─ Daily Nielsen Scores ─┐  ┌─ Error Categories ─┐
│ Line chart (7 days)    │  │ Pie chart          │
│ Target line at 85%     │  │ Top 5 issue types  │
└───────────────────────┘  └───────────────────┘

┌─ Processing Time Trends ─┐  ┌─ Team Performance ─┐  
│ Bar chart (30 days)      │  │ Completion rates    │
│ Goal: <5min per file     │  │ By user/role        │
└─────────────────────────┘  └────────────────────┘
```

### 2.5 Settings/Configuration (`/settings`)

**Layout**: Tabbed interface

**Tabs**:
- Validation Rules
- Export Preferences  
- Team Management
- API Configuration
- Notification Settings

---

## 3. Component Library

### 3.1 Core Components

#### Status Indicators
```css
.status-success { color: #28a745; }
.status-warning { color: #ffc107; }
.status-error { color: #dc3545; }
.status-processing { color: #007bff; }
```

#### Nielsen Score Display
```html
<div class="nielsen-score">
  <div class="score-value">87%</div>
  <div class="score-bar">
    <div class="score-fill" style="width: 87%"></div>
  </div>
  <div class="score-breakdown">
    <span>Required: 94%</span>
    <span>Optional: 73%</span>
    <span>Recommended: 89%</span>
  </div>
</div>
```

#### Issue Card Template
```html
<div class="issue-card severity-critical">
  <div class="issue-header">
    <span class="issue-icon">📍</span>
    <h3 class="issue-title">Missing Required ISBN</h3>
    <span class="issue-location">Line 247</span>
  </div>
  <div class="issue-body">
    <p class="issue-description">...</p>
    <div class="issue-solution">...</div>
    <div class="issue-example">...</div>
  </div>
  <div class="issue-actions">
    <button class="btn-secondary">View Context</button>
    <button class="btn-primary">Mark Resolved</button>
  </div>
</div>
```

#### Progress Indicators
```html
<div class="validation-progress">
  <div class="step completed">
    <span class="step-icon">✓</span>
    <span class="step-label">XSD Validation</span>
  </div>
  <div class="step active">
    <span class="step-icon">⏳</span>
    <span class="step-label">Rule Engine</span>
  </div>
  <div class="step pending">
    <span class="step-icon">⏸</span>
    <span class="step-label">Schematron</span>
  </div>
</div>
```

### 3.2 Data Visualization Components

#### Chart Requirements (Tufte Principles)
- Remove chart borders and gridlines
- Minimal color palette (3-4 colors max)
- Direct data labeling instead of legends
- High data-ink ratio
- No 3D effects or unnecessary decoration

#### Nielsen Score Trend Chart
```javascript
// D3.js implementation template
const nielsenChart = {
  width: 600,
  height: 200,
  margin: { top: 20, right: 30, bottom: 40, left: 40 },
  targetLine: 85, // Publisher's target score
  xAxis: 'date',
  yAxis: 'nielsen_score',
  showTarget: true,
  showTrend: true
}
```

#### Error Category Distribution
```javascript
const errorPieChart = {
  maxSlices: 5, // Show top 5, group rest as "Other"
  showPercentages: true,
  directLabeling: true, // Labels on slices, not legend
  colors: ['#dc3545', '#fd7e14', '#ffc107', '#6c757d', '#dee2e6']
}
```

---

## 4. Responsive Design Requirements

### 4.1 Breakpoints
- Desktop: 1200px+
- Tablet: 768px - 1199px  
- Mobile: 320px - 767px (view-only, no editing)

### 4.2 Layout Adaptations

#### Desktop (1200px+)
- Three-column layout on results dashboard
- Side-by-side charts in analytics
- Full table views with all columns
- Hover states and detailed tooltips

#### Tablet (768px-1199px)  
- Two-column layout, collapsible sidebar
- Stacked charts in analytics
- Horizontal scrolling for wide tables
- Touch-optimized buttons (44px minimum)

#### Mobile (320px-767px)
- Single column, navigation drawer
- View-only mode for results
- Card-based layout for issues
- Essential information only

### 4.3 Touch Considerations
- Minimum 44px touch targets
- Swipe gestures for navigation
- Pull-to-refresh on lists
- Long-press for context menus

---

## 5. Data Visualization Requirements

### 5.1 Nielsen Score Visualization

#### Primary Display
- Large percentage (48px font)
- Horizontal progress bar
- Color coding: Red (<70%), Yellow (70-84%), Green (85%+)
- Breakdown by category (Required/Optional/Recommended)

#### Trend Visualization  
- 7-day or 30-day line chart
- Target line overlay
- Annotations for significant changes
- Zoom/pan capabilities

### 5.2 Error Reporting Visualization

#### Issue Severity Hierarchy
1. **Critical**: Red, blocking icon, top priority
2. **Warning**: Yellow, attention icon, medium priority  
3. **Info**: Blue, info icon, low priority
4. **Recommendation**: Green, suggestion icon, enhancement

#### Error Trend Analysis
- Daily error counts by category
- Resolution time metrics
- Before/after Nielsen score impact
- Team performance indicators

### 5.3 KPI Dashboard

#### Key Metrics
- Processing time: Target <5 minutes
- Nielsen score: Target 85%+
- Error resolution rate: Target 95%
- Time saved vs manual process

#### Visualization Types
- Sparklines for trends
- Gauge charts for targets
- Heat maps for team performance
- Bullet charts for goal tracking

---

## 6. Technical Implementation Notes

### 6.1 Frontend Framework Recommendation

**Primary**: Vue.js 3 with Composition API
- Reactive data binding for real-time updates
- Component-based architecture
- Good performance with large data sets
- TypeScript support

**Alternative**: React with TypeScript
- Large ecosystem
- Server-side rendering capabilities
- Strong community support

### 6.2 UI Component Libraries

**Primary**: Tailwind CSS + Headless UI
- Utility-first approach
- Customizable design system
- Accessible components
- Small bundle size

**Alternative**: Material-UI or Ant Design
- Pre-built business components
- Consistent design system
- Built-in accessibility

### 6.3 Data Visualization

**Charts**: D3.js or Chart.js
- Custom Tufte-compliant styling
- Real-time data updates
- Export capabilities
- Responsive design

**Tables**: TanStack Table (formerly React Table)
- Virtual scrolling for large datasets
- Sorting, filtering, pagination
- Column resizing and reordering
- Export functionality

### 6.4 API Integration Points

#### Endpoints Required
```javascript
// File upload and processing
POST /api/v1/validate
GET /api/v1/jobs/:jobId/status
GET /api/v1/jobs/:jobId/results

// Batch operations
GET /api/v1/jobs
POST /api/v1/batch/validate
GET /api/v1/analytics/dashboard

// Configuration
GET /api/v1/rules
PUT /api/v1/rules/:ruleId
GET /api/v1/settings
```

#### WebSocket Requirements
```javascript
// Real-time updates
ws://api.example.com/jobs/:jobId/stream
- Validation progress updates
- Error discovery notifications  
- Completion status
- Log streaming
```

### 6.5 State Management

**Recommended**: Zustand or Pinia
- Simple API
- TypeScript support
- DevTools integration
- Minimal boilerplate

**State Structure**:
```javascript
{
  jobs: {
    active: [],
    completed: [],
    current: null
  },
  validation: {
    rules: [],
    settings: {},
    results: null
  },
  ui: {
    sidebarOpen: true,
    selectedTab: 'issues',
    filters: {}
  }
}
```

### 6.6 Performance Requirements

- Initial page load: <2 seconds
- File upload processing start: <5 seconds
- Real-time updates: <500ms latency
- Chart rendering: <1 second
- Table sorting/filtering: <300ms

### 6.7 Accessibility Requirements

- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management for SPAs

### 6.8 Browser Support

- Chrome 90+ (primary)
- Firefox 88+
- Safari 14+
- Edge 90+
- No Internet Explorer support

---

## 7. Development Phases

### Phase 1: Core Validation Workflow (Week 1-2)
- Upload screen
- Processing status
- Basic results display
- Essential error reporting

### Phase 2: Enhanced UX (Week 3-4)  
- Advanced filtering
- Detailed error guidance
- Nielsen score visualization
- Export functionality

### Phase 3: Analytics & Batch Processing (Week 5-6)
- Dashboard analytics
- Batch processing interface
- Team performance metrics
- Advanced configuration

### Phase 4: Polish & Optimization (Week 7-8)
- Responsive design implementation
- Performance optimization
- Accessibility audit
- User testing feedback integration

---

## 8. Success Criteria

### Quantitative Metrics
- Reduce validation time from 30-60 minutes to <5 minutes
- Achieve 95% error detection accuracy
- Support 50+ concurrent validations
- Maintain <2 second page load times

### Qualitative Metrics
- Users can understand critical errors within 60 seconds
- Error resolution guidance is actionable and clear
- Nielsen score improvement is trackable
- Interface feels professional and trustworthy

### User Acceptance Criteria
- Production managers can monitor team performance
- Metadata editors can resolve errors without technical support
- Technical staff can access raw validation data
- All users can export results in required formats

---

*This specification is a living document and should be updated based on user feedback and development constraints.*