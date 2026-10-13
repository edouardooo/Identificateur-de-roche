-- Base de données de la photothèque (Supabase).
--
-- À exécuter UNE SEULE FOIS : dans le tableau de bord Supabase, menu « SQL Editor »,
-- « New query », coller tout ce fichier puis cliquer sur « Run ».
-- Le script peut être relancé sans danger : il ne recrée pas ce qui existe déjà.

-- Extension pour comparer les empreintes des photos (utilisée à l'étape 3 du plan)
create extension if not exists vector with schema extensions;

-- Une ligne par photo envoyée
create table if not exists public.photos (
  id uuid primary key default gen_random_uuid(),
  cree_le timestamptz not null default now(),
  chemin_image text not null,                     -- emplacement du fichier dans le stockage « photos »
  empreinte_fichier text not null unique,         -- SHA-256 du fichier envoyé, pour refuser les doublons
  embedding extensions.vector(384),               -- empreinte DINOv2 (étape 3 du plan)
  prediction text,                                -- roche proposée par le modèle (étape 3)
  score_prediction real,
  roche_proposee text,                            -- réponse du visiteur
  source_etiquette text not null default 'inconnue'
    check (source_etiquette in ('inconnue', 'liste', 'cle', 'suggestion')),
  statut text not null default 'a_verifier'
    check (statut in ('a_verifier', 'validee', 'rejetee')),
  roche_validee text,                             -- décision de l'administrateur
  validee_le timestamptz,
  contributeur text,                              -- nom ou pseudo, facultatif
  origine text not null default 'contribution',   -- contribution, wikimedia commons, ens lyon...
  auteur text,                                    -- auteur à citer si la photo vient d'ailleurs
  licence text not null default 'CC BY 4.0',
  consentement boolean not null check (consentement)
);

create index if not exists photos_statut_idx on public.photos (statut, cree_le);
create index if not exists photos_roche_idx on public.photos (roche_validee) where statut = 'validee';
create index if not exists photos_embedding_idx on public.photos
  using hnsw (embedding extensions.vector_cosine_ops);

-- Personne n'accède directement à la table depuis internet : seul le site, avec la
-- clé secrète gardée dans les secrets Streamlit, peut lire et écrire.
alter table public.photos enable row level security;
grant select, insert, update, delete on public.photos to service_role;

-- Nombre de photos validées pour chaque roche (page Photothèque)
create or replace function public.nombre_photos_validees()
returns table (roche text, nombre bigint)
language sql stable
set search_path = public
as $$
  select roche_validee, count(*) from public.photos
  where statut = 'validee' group by roche_validee;
$$;

-- Photos validées les plus ressemblantes à une empreinte (étape 3 du plan)
create or replace function public.photos_proches(requete extensions.vector(384), nombre int default 10)
returns table (id uuid, roche text, chemin_image text, similarite real)
language sql stable
set search_path = public, extensions
as $$
  select id, roche_validee, chemin_image, (1 - (embedding <=> requete))::real
  from public.photos
  where statut = 'validee' and embedding is not null
  order by embedding <=> requete
  limit nombre;
$$;

revoke execute on function public.nombre_photos_validees() from public, anon, authenticated;
revoke execute on function public.photos_proches(extensions.vector, int) from public, anon, authenticated;
grant execute on function public.nombre_photos_validees() to service_role;
grant execute on function public.photos_proches(extensions.vector, int) to service_role;

-- Stockage privé des fichiers : les photos ne sont visibles que par des liens
-- temporaires créés par le site, et seulement une fois validées.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('photos', 'photos', false, 5242880, array['image/jpeg'])
on conflict (id) do nothing;
