# Table queries - Hyena Hostable

### 1. action-logs.sqlite

```sql
CREATE TABLE "moderation_actions" (
	"user_id"	INTEGER,
	"actions"	TEXT,
	PRIMARY KEY("user_id")
);
```