# Quarterly Physicals Reporting System

A comprehensive quarterly reporting cycle system for physical assessments with automatic quarter assignment, scoring, and reporting capabilities.

## System Overview

```mermaid
flowchart TB
    Start[New Assessment Entry] --> CheckDate{Has submission_date?}
    CheckDate -->|No| GetLast[Get Last Assessment Date]
    CheckDate -->|Yes| AssignQuarter[Find Closest Quarter Cycle]
    GetLast --> AssignQuarter
    AssignQuarter --> CalcAge[Calculate Age at Assessment]
    CalcAge --> ScoreTests[Calculate Test Scores]
    ScoreTests --> Store[Store in member_physicals_raw]
    Store --> Report[Quarterly Reports & Views]
    
    style Start fill:#e1f5ff
    style Store fill:#c8e6c9
    style Report fill:#fff9c4
```

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph Input["📥 Input Sources"]
        Manual[Manual Entry]
        Import[CSV Import]
        API[API/Form]
    end
    
    subgraph Processing["⚙️ Processing Layer"]
        Trigger[Auto Calculate Trigger]
        QuarterFunc[Quarter Assignment]
        ScoreFunc[Score Calculation]
    end
    
    subgraph Storage["💾 Database Tables"]
        Raw[member_physicals_raw]
        Cycles[physicals_quarterly_cycles]
        Lookup[physicals_scoring_lookup]
        Members[member_database]
    end
    
    subgraph Output["📊 Output & Reporting"]
        Summary[view_physicals_quarterly_summary]
        Due[view_members_due_for_assessment]
        Rollup[Rollup Functions]
    end
    
    Input --> Processing
    Processing --> Storage
    Storage --> Output
    
    style Input fill:#e3f2fd
    style Processing fill:#fff3e0
    style Storage fill:#f3e5f5
    style Output fill:#e8f5e9
```

## Quarterly Cycle Assignment Flow

```mermaid
sequenceDiagram
    participant User
    participant System
    participant Trigger
    participant QuarterFunc
    participant Cycles
    participant Storage
    
    User->>System: Create Assessment<br/>(with/without date)
    System->>Trigger: INSERT member_physicals_raw
    Trigger->>Trigger: Check submission_date
    alt submission_date is NULL
        Trigger->>Trigger: Get last assessment date
    end
    Trigger->>QuarterFunc: get_quarter_cycle_for_date()
    QuarterFunc->>Cycles: Find closest cycle_date
    Cycles-->>QuarterFunc: Return cycle_id
    QuarterFunc-->>Trigger: cycle_id
    Trigger->>Trigger: Calculate scores
    Trigger->>Storage: Store with quarter_cycle_id
    Storage-->>User: Assessment saved
```

## Database Schema Relationships

```mermaid
erDiagram
    member_database ||--o{ member_physicals_raw : "has"
    physicals_quarterly_cycles ||--o{ member_physicals_raw : "assigned to"
    staff_database ||--o{ member_physicals_raw : "coach"
    member_memberships ||--o{ member_physicals_raw : "membership"
    physicals_scoring_lookup ||--o{ member_physicals_raw : "scores"
    
    member_physicals_raw {
        uuid id PK
        uuid member_id FK
        uuid quarter_cycle_id FK
        uuid coach_id FK
        uuid membership_id FK
        date submission_date
        integer age_at_assessment
        numeric grip_strength_value
        numeric grip_strength_score
        numeric push_ups_value
        numeric push_ups_score
        numeric vo2_value
        numeric vo2_score
    }
    
    physicals_quarterly_cycles {
        uuid id PK
        text cycle_name
        date cycle_date
        integer cycle_year
        integer quarter_number
        text description
    }
    
    physicals_scoring_lookup {
        uuid id PK
        text test_name
        text gender
        integer age_min
        integer age_max
        numeric raw_value
        numeric score
    }
```

## Assessment Processing Pipeline

```mermaid
flowchart TD
    A[Assessment Created] --> B{Submission Date?}
    B -->|NULL| C[Get Last Assessment Date]
    B -->|Provided| D[Use Provided Date]
    C --> D
    D --> E[Find Closest Quarter Cycle]
    E --> F[Get Member DOB & Gender]
    F --> G[Calculate Age at Assessment]
    G --> H{Test Values Provided?}
    H -->|Yes| I[Lookup Scores from physicals_scoring_lookup]
    H -->|No| J[Skip Score Calculation]
    I --> K[Store All Values & Scores]
    J --> K
    K --> L[Auto-assign quarter_cycle_id]
    L --> M[Assessment Complete]
    
    style A fill:#e1f5ff
    style M fill:#c8e6c9
    style I fill:#fff9c4
```

## Quarterly Reporting Flow

```mermaid
flowchart LR
    subgraph Data["📋 Raw Data"]
        Raw[member_physicals_raw<br/>All Assessments]
    end
    
    subgraph Processing["🔄 Processing"]
        Filter[Filter by quarter_cycle_id]
        Latest[Get Most Recent<br/>per member/cycle]
        Aggregate[Calculate Averages]
    end
    
    subgraph Views["👁️ Reporting Views"]
        Summary[view_physicals_quarterly_summary<br/>Quarterly Reports]
        Due[view_members_due_for_assessment<br/>Reminder List]
    end
    
    subgraph Functions["🔧 Helper Functions"]
        Rollup[get_quarterly_rollup<br/>Member/Quarter Details]
        Status[get_cycle_completion_status<br/>Completion Stats]
    end
    
    Raw --> Filter
    Filter --> Latest
    Latest --> Aggregate
    Aggregate --> Summary
    Aggregate --> Due
    Latest --> Rollup
    Latest --> Status
    
    style Data fill:#e3f2fd
    style Processing fill:#fff3e0
    style Views fill:#e8f5e9
    style Functions fill:#f3e5f5
```

## Yearly Cycle Generation

```mermaid
flowchart TB
    Cron[pg_cron Job<br/>Dec 1st Annually] --> NextYear[Get Next Year]
    NextYear --> BaseDates[Base Dates:<br/>Mar 9, Jun 15,<br/>Sep 7, Dec 7]
    BaseDates --> FindMonday[Find Closest Monday<br/>for Each Date]
    FindMonday --> CheckExists{Cycles Exist<br/>for Year?}
    CheckExists -->|Yes| Skip[Skip Generation]
    CheckExists -->|No| Create[Create 4 Cycles]
    Create --> Store[Store in<br/>physicals_quarterly_cycles]
    Store --> Ready[Cycles Ready<br/>for Next Year]
    
    style Cron fill:#e1f5ff
    style Ready fill:#c8e6c9
    style Skip fill:#ffebee
```

## Score Calculation Flow

```mermaid
flowchart TD
    Start[Test Value Entered] --> GetMember[Get Member Info:<br/>DOB, Gender]
    GetMember --> CalcAge[Calculate Age<br/>at Assessment]
    CalcAge --> AgeGroup{Determine<br/>Age Group}
    AgeGroup -->|U40| U40[Age < 40]
    AgeGroup -->|40-54| Mid[Age 40-54]
    AgeGroup -->|55+| Over55[Age 55+]
    U40 --> Lookup[Lookup Score in<br/>physicals_scoring_lookup]
    Mid --> Lookup
    Over55 --> Lookup
    Lookup --> Match{Exact<br/>Match?}
    Match -->|Yes| Return[Return Score]
    Match -->|No| Closest[Find Closest<br/>or Cap at Min/Max]
    Closest --> Return
    Return --> Store[Store Score<br/>in Assessment]
    
    style Start fill:#e1f5ff
    style Store fill:#c8e6c9
    style Lookup fill:#fff9c4
```

## Key Features

- ✅ **Automatic Quarter Assignment**: Assessments automatically assigned to closest quarterly cycle
- ✅ **Smart Defaults**: Submission date defaults to last assessment if not provided
- ✅ **Auto-Scoring**: All test scores calculated automatically from lookup tables
- ✅ **Most Recent Only**: Reporting uses most recent assessment per member per quarter
- ✅ **Yearly Automation**: Cycles auto-generated for following year via cron job
- ✅ **Monday Adjustment**: Cycle dates automatically adjusted to closest Monday

## Database Tables

| Table | Purpose |
|-------|---------|
| `member_physicals_raw` | Stores all physical assessments with values and scores |
| `physicals_quarterly_cycles` | Defines quarterly cycle dates and metadata |
| `physicals_scoring_lookup` | Lookup table for converting raw values to scores (0-10) |
| `member_database` | Member information (DOB, gender, etc.) |

## Views & Functions

| Component | Purpose |
|-----------|---------|
| `view_physicals_quarterly_summary` | Quarterly summary with most recent assessments |
| `view_members_due_for_assessment` | Active members needing assessments |
| `get_quarterly_rollup()` | Get detailed rollup for member/quarter |
| `get_cycle_completion_status()` | Get completion statistics for a cycle |

## Usage

### Create Assessment
```sql
INSERT INTO member_physicals_raw (member_id, submission_date, grip_strength_value, ...)
VALUES (...);
-- Quarter and scores automatically assigned!
```

### View Quarterly Summary
```sql
SELECT * FROM view_physicals_quarterly_summary 
WHERE cycle_year = 2026 AND quarter_number = 1;
```

### Get Members Due
```sql
SELECT * FROM view_members_due_for_assessment;
```

## Quarterly Cycles (2026)

- **Q1**: March 9, 2026 - Post-New Year execution phase
- **Q2**: June 13, 2026 - Financial + physical accountability (EOFY)
- **Q3**: September 7, 2026 - Post-winter slump reset
- **Q4**: December 7, 2026 - Q4 Assessment Cycle

## Automation

- **Cron Job**: Runs annually on December 1st to generate next year's cycles
- **Trigger**: Auto-calculates scores and assigns quarters on insert/update
- **Default Dates**: Automatically uses last assessment date if not provided

