drop table if exists users cascade;
drop table if exists transportations cascade;
drop type if exists transportation_mode_enum cascade;
drop type if exists accomodation_category_enum cascade;
drop table if exists transportations cascade;
drop table if exists accomodations cascade;
drop table if exists sites;
drop type if exists site_category_enum;

create type accomodation_category_enum as enum ('LUXURY', 'MIDRANGE', 'BUDGET');
create type transportation_mode_enum as enum ('CAR','TRAIN','AIRPLANE','BUS');
create type site_category_enum as enum ('HISTORICAL','NATURAL_WONDER','CULTURAL_ATTRACTION','ADVENTURE_SPOT');

create table users (
    id uuid primary key,
    name varchar(255) not null,
    email varchar(255) not null,
    password varchar(255) not null
);

create table sites (
    id uuid primary key,
    name varchar(255) not null,
    category site_category_enum not null,
    description varchar(255) not null,
    location varchar(255) not null,
);

create table transportations (
    id uuid primary key,
    site_id uuid references sites(id) not null,
    company varchar(255) not null,
    cost int not null,
    mode transportation_mode_enum not null
);

create table accomodations (
    id uuid primary key,
    site_id uuid references sites(id) not null,
    company varchar(255) not null,
    category accomodation_category_enum not null,
    cost float not null
);

