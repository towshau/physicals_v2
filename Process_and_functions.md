# Process & functions

How physicals assessments get into the system and how the main functions and tables fit together.

---

## Assessment sources

Assessments in *member_physicals_raw* come from two places:

| Source | When | *source* value |
|--------|------|----------------|
| **Form** | Manual entry (UI / import) | `form` (default) |
| **Team Builder** | Sync from workout results | `tb` |

*Table: *member_physicals_raw*. Column: *source* (text).*

---

## High-level flow

```mermaid
flowchart LR
  subgraph inputs [Inputs]
    Form[Form / manual]
    TB[Team Builder]
  end
  
  subgraph storage [Storage]
    Raw[member_physicals_raw]
  end
  
  Form -->|"source = form"| Raw
  TB -->|"sync_tb_physicals_to_member_physicals_raw()"| Raw
  Raw --> Trigger[Triggers: scores, quarter, membership]
  
  style Form fill:#e3f2fd
  style TB fill:#fff3e0
  style Raw fill:#e8f5e9
```

*Inserts into *member_physicals_raw* fire *auto_populate_membership_id* and *auto_calculate_physicals_scores* (scores, age, quarter).*

---

## Form path (manual entry)

```mermaid
flowchart TD
  A[User submits form] --> B[INSERT member_physicals_raw]
  B --> C["source defaults to 'form'"]
  C --> D[Triggers run]
  D --> E[Quarter + scores set]
  
  style A fill:#e1f5ff
  style E fill:#c8e6c9
```

*No extra logic; *source* stays `form`.*

---

## Team Builder sync path

```mermaid
flowchart TD
  Start[Run sync] --> Read[Read member_tbresults]
  Read --> Filter["exercise_name ILIKE '%Physicals Test%'"]
  Filter --> Agg[Aggregate by member_id, completed_date]
  Agg --> Map[Map test names to columns]
  Map --> Upsert{Row exists for member + date?}
  Upsert -->|Yes| Update[UPDATE with new values, source = 'tb']
  Upsert -->|No| Insert[INSERT new row, source = 'tb']
  Update --> Done[Triggers run]
  Insert --> Done
  Done --> Scores[Scores and quarter set]
  
  style Start fill:#e1f5ff
  style Scores fill:#c8e6c9
```

*Function: *sync_tb_physicals_to_member_physicals_raw()*. Reads from *member_tbresults*; writes to *member_physicals_raw* with *source* = `tb`.*

---

## Sync function: data flow

```mermaid
flowchart LR
  subgraph source [Source]
    TB[member_tbresults]
  end
  
  subgraph func [Function]
    F[sync_tb_physicals_to_member_physicals_raw]
  end
  
  subgraph helpers [Helpers]
    G[get_active_membership_id]
    M[member_memberships]
  end
  
  subgraph target [Target]
    Raw[member_physicals_raw]
  end
  
  TB --> F
  F --> G
  G --> M
  F --> Raw
```

*Sync uses *get_active_membership_id(member_id, completed_date)* and *member_memberships.coach_id* for membership and coach.*

---

## Sync: test name → column (summary)

| Name contains (ILIKE) | Column written |
|------------------------|----------------|
| push up / push-up | *push_ups_value* |
| vertical jump | *vertical_jump_value* |
| chin hold | *chin_hold_value* |
| grip + left/right | *grip_strength_left* / *grip_strength_right* |
| grip (no side) | *grip_strength_value* |
| lateral hop + left/right | *left_lateral_hop* / *right_lateral_hop* |
| vo2 | *vo2_value* |
| rsi | *rsi_value* |
| concept2 | *concept2_value* |

*Only rows with “Physicals Test” in *exercise_name* are synced. Values from *reps* or *result* depending on test.*

---

## One row per member per date

```mermaid
flowchart TD
  A[member_id + completed_date] --> B{Existing row?}
  B -->|"match on member_id and created_at::date"| C[UPDATE]
  B -->|No match| D[INSERT with created_at = workout date]
  C --> E[Single assessment row]
  D --> E
```

*Sync keeps one *member_physicals_raw* row per member per workout date; later syncs update that row.*

---

## Key tables & functions

| Item | Role |
|------|------|
| *member_physicals_raw* | All assessments; *source* = `form` or `tb`. |
| *member_tbresults* | Team Builder exercise results; source for TB sync. |
| *member_memberships* | Active membership and *coach_id* for sync. |
| *sync_tb_physicals_to_member_physicals_raw()* | Syncs Physicals Test rows into *member_physicals_raw*; sets *source* = `tb`. |
| *get_active_membership_id(member_id, date)* | Returns active membership for that date. |
| *auto_calculate_physicals_scores* | Trigger: age, quarter, scores from *physicals_scoring_lookup*. |
| *auto_populate_membership_id* | Trigger: fills *membership_id* if NULL on insert. |

*Run *sync_tb_physicals_to_member_physicals_raw()* on a schedule or on-demand to pull new TB physicals.*
