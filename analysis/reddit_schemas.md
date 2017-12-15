### SQL

```
    create_table_sql = {
        'authors': '''CREATE TABLE authors (name VARCHAR(250) NOT NULL UNIQUE);''',
        'subreddits': '''CREATE TABLE subreddits (name VARCHAR(250) NOT NULL UNIQUE);''',
        'comments': '''
    CREATE TABLE comments(
                        permalink VARCHAR(800) NOT NULL UNIQUE,
                        id VARCHAR(250) NOT NULL,
                        author VARCHAR(250) NOT NULL,
                        subreddit VARCHAR(25) NOT NULL,
                        subreddit_id VARCHAR(25) NOT NULL,
                        name VARCHAR(25) NOT NULL,
                        parent_id VARCHAR(25),
                        depth INTEGER DEFAULT 0,
                        body TEXT NOT NULL,
                        score INTEGER DEFAULT 0,
                        ups INTEGER DEFAULT 0,
                        downs INTEGER DEFAULT 0,
                        controversiality INTEGER DEFAULT 0,
                        user_reports TEXT,
                        created_utc INTEGER NOT NULL,
                        label INTEGER DEFAULT 0, 
                        FOREIGN KEY (author) REFERENCES authors (name),
                        FOREIGN KEY (subreddit) REFERENCES subreddits (name)
                        );
    ''',
        'submissions': '''
    CREATE TABLE submissions (permalink VARCHAR(800) NOT NULL UNIQUE,
                          id VARCHAR(250) NOT NULL,
                          name VARCHAR(25) NOT NULL,
                          title text NOT NULL,
                          author VARCHAR(250) NOT NULL,
                          subreddit VARCHAR(250) NOT NULL,
                          user_reports TEXT,
                          created_utc INTEGER NOT NULL,
                          downs INTEGER DEFAULT 0,
                          url VARCHAR(250),
                          ups INTEGER DEFAULT 0,
                          comment_limit INTEGER DEFAULT 0,
                          score INTEGER DEFAULT 0,
                          upvote_ratio NUMERIC,
                          over_18 BOOLEAN,
                          brand_safe BOOLEAN,
                          num_comments INTEGER DEFAULT 0,
                        FOREIGN KEY (author) REFERENCES authors (name),
                        FOREIGN KEY (subreddit) REFERENCES subreddits (name)
                          );
                          '''
    }
```

### Various Notes:

Comments:

When a comment's `name` matches another comment `parent_id` then the comment is parent of that comment. The comment's `depth` indicates how many deep it is sorted by `created_utc`.
