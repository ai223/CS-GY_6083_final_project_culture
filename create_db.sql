create schema if not exists culture;

drop table if exists culture.has_event;
drop table if exists culture.MuseumEvent;
drop table if exists culture.created_by;
drop table if exists culture.MuseumObjectCreator;
drop table if exists culture.has_object_MuseumObject;
drop table if exists culture.located_at_Museum;

drop table if exists culture.has_actor;
drop table if exists culture.has_screenwriter;
drop table if exists culture.FilmScreenwriter;
drop table if exists culture.FilmActor;
drop table if exists culture.showing_at;
drop table if exists culture.FilmScreening;
drop table if exists culture.has_location_FilmTheater;
drop table if exists culture.has_director_Film;
drop table if exists culture.FilmDirector;

drop table if exists culture.Location;

create table culture.Location(
	lid			integer		primary key,
	country		varchar(64),
	borough		varchar(32),
	zip			integer,
	poBox		integer,
	latitude	decimal,
	longitude	decimal
);

-- Museum Section

create table culture.located_at_Museum(
	mid 	integer		primary key,
	name	varchar(128),
	type	varchar(64),
	lid	integer		not null,
	foreign key (lid) references culture.Location(lid)
);

create table culture.has_object_MuseumObject(
	moid			integer		primary key,
	name			varchar(128),
	period			varchar(64),
	style			varchar(64),
	date			date,
	country			varchar(64),
	popularityRank	integer,
	mid				integer 	not null,
	foreign key (mid) references culture.located_at_Museum(mid)
);

create table culture.MuseumObjectCreator(
	mocid		integer		primary key,
	name		varchar(128),
	period		varchar(64),
	style		varchar(64),
	birthCountry	varchar(64),
	dob		date,
	dod		date
);

create table culture.created_by(
	moid		integer,
	mocid 		integer,
	primary key (moid, mocid),
	foreign key (moid) references culture.has_object_MuseumObject(moid),
	foreign key (mocid) references culture.MuseumObjectCreator(mocid)
);

create table culture.MuseumEvent(
	meid		integer		primary key,
	url			varchar(128),
	name		varchar(64),
	startDate	timestamp,
	endDate		timestamp,
	price		decimal,
	subject		varchar(256)
);

create table culture.has_event(
	mid		integer,
	meid	integer,
	primary key(mid, meid),
	foreign key (mid) references culture.located_at_Museum(mid),
	foreign key (meid) references culture.MuseumEvent(meid)
);

-- Film Section

create table culture.has_location_FilmTheater(
	ftid		integer		primary key,
	name		varchar(128),
	ticketPrice	decimal,
	lid		integer		not null,
	foreign key (lid) references culture.Location(lid)
);

create table culture.FilmScreening(
	fsid		integer		primary key,
	starttime	timestamp,
	roomNum		integer
);

create table culture.FilmDirector(
	fdid	integer		primary key,
	name	varchar(128),
	dob		date,
	dod		date
);

create table culture.has_director_Film(
	fid			integer		primary key,
	name		varchar(128),
	year		integer,
	genre		varchar(64),
	fdid		integer		not null,
	foreign key (fdid) references culture.FilmDirector
);

create table culture.showing_at(
	fid		integer,
	fsid	integer,
	ftid	integer,
	primary key (fid, fsid, ftid),
	foreign key (fid) references culture.has_director_Film(fid),
	foreign key(fsid) references culture.FilmScreening(fsid),
	foreign key(ftid) references culture.has_location_FilmTheater(ftid)
);

create table culture.FilmActor(
	faid	integer		primary key,
	name	varchar(128),
	dob		date,
	dod		date
);

create table culture.has_actor(
	faid	integer,
	fid		integer,
	primary key (faid, fid),
	foreign key (faid) references culture.FilmActor(faid),
	foreign key (fid) references culture.has_director_Film(fid)
);

create table culture.FilmScreenwriter(
	fscid 	integer		primary key,
	name	varchar(128),
	dob		date,
	dod		date
);

create table culture.has_screenwriter(
	fscid	integer,
	fid		integer,
	primary key (fscid , fid),
	foreign key (fscid ) references culture.FilmScreenwriter(fscid),
	foreign key (fid) references culture.has_director_Film(fid)
);

-- add statements to ingest data 
