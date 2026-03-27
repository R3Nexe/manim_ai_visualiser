-- ── 1. Add match_threshold parameter to the RPC ──────────────────────────────
--    Drop the old version first (Postgres requires this when the signature changes)
drop function if exists match_manim_examples(vector, int);

create or replace function match_manim_examples(
    query_embedding  vector(384),
    match_count      int     default 3,
    match_threshold  float   default 0.30   -- tune this after you see real scores
)
returns table (
    id          bigint,
    title       text,
    description text,
    code        text,
    similarity  float
)
language sql stable
as $$
    select
        id,
        title,
        description,
        code,
        1 - (embedding <=> query_embedding) as similarity
    from manim_examples
    where 1 - (embedding <=> query_embedding) > match_threshold
    order by embedding <=> query_embedding
    limit match_count;
$$;


-- ── 2. Add a concepts column so you can store + filter by topic ───────────────
--    (optional but helps a lot for debugging what was embedded)
alter table manim_examples
    add column if not exists concepts text default '';

alter table manim_examples
    add column if not exists visual_elements text default '';

alter table manim_examples
    add column if not exists difficulty text default 'intermediate';


-- ── 3. Prevent duplicate inserts when you re-run store_all_scenes() ──────────
--    Without this, every embed run doubles your table.
alter table manim_examples
    add column if not exists source_file text default '';

create unique index if not exists manim_examples_source_file_idx
    on manim_examples (source_file)
    where source_file <> '';


-- ── 4. Verify everything looks right ─────────────────────────────────────────
select
    indexname,
    indexdef
from pg_indexes
where tablename = 'manim_examples';