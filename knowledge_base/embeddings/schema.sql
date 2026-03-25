-- Run this once in your Supabase SQL editor to set up the knowledge base.

-- Enable pgvector extension
create extension if not exists vector;

-- Manim code examples table
create table if not exists manim_examples (
    id          bigserial primary key,
    title       text        not null,
    description text        not null,
    code        text        not null,
    embedding   vector(384),
    created_at  timestamptz default now()
);

-- HNSW index for cosine similarity search (works at any table size;
-- prefer over ivfflat which needs ~3200+ rows to function correctly)
create index if not exists manim_examples_embedding_idx
    on manim_examples using hnsw (embedding vector_cosine_ops);

-- Stored procedure called by retriever.py
create or replace function match_manim_examples(
    query_embedding vector(384),
    match_count     int default 3
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
    order by embedding <=> query_embedding
    limit match_count;
$$;
