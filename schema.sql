-- Database Schema for AI Emoji Maker
-- Execute this script in your Supabase Dashboard -> SQL Editor

-- Drop tables if re-initializing schema
DROP TABLE IF EXISTS public.image_generations CASCADE;
DROP TABLE IF EXISTS public.profiles CASCADE;

-- 1. Create profiles table to store user subscription and usage details
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    plan_type TEXT DEFAULT 'Free' NOT NULL,
    generations_used INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Create image_generations table to store metadata for user generated emojis
CREATE TABLE public.image_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    original_prompt TEXT NOT NULL,
    final_prompt TEXT NOT NULL,
    image_url TEXT NOT NULL,
    image_size TEXT NOT NULL,
    style TEXT DEFAULT 'Sticker',
    mood TEXT DEFAULT 'Happy',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_profiles_email ON public.profiles(email);
CREATE INDEX IF NOT EXISTS idx_image_generations_user_id ON public.image_generations(user_id);
