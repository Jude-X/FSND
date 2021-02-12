import json
import dateutil.parser
import babel
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form, FlaskForm
from forms import *
from flask_migrate import Migrate
import psycopg2
from app import app, db
from models import Venue, Artist, Shows




@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    all_venues = Venue.query.group_by(Venue.id, Venue.city).all()
    data = []
    current_city = "null"
    # Looping over each venue in the database
  for venue in all_venues:
    if current_city == venue.city:
      data[len(data) - 1]["venues"].append({
        "id": venue.id,
        "name":venue.name,
        "num_upcoming_shows": 0 
      })
    else:
      data.append({
        "city":venue.city,
        "state":venue.state,
        "venues": [{
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": 0
        }]
      })
      current_city = venue.city
    
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    
    venue_select = Venue.query
    venue_list = []

    venues = venue_select.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))

    for venue in venues:
        venue_list.append({
        "id":venue.id,
        "name":venue.name,
        "num_upcoming_shows": 0,
        })

    response={
        "count": len(venue_list),
        "data": venue_list
    }
        
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue_in_view = Venue.query.get(venue_id)
    data = {
    "id": venue_in_view.id,
    "name": venue_in_view.name,
    "genres": venue_in_view.genres,
    "address": venue_in_view.address,
    "city": venue_in_view.city,
    "state": venue_in_view.state,
    "phone": venue_in_view.phone,
    "website": venue_in_view.website,
    "facebook_link": venue_in_view.facebook_link,
    "seeking_talent": venue_in_view.seeking_talent,
    "image_link": venue_in_view.image_link
    }
    
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET','POST'])
def create_venue_form():
    if request.method == 'GET':
        form = VenueForm()
        return render_template('forms/new_venue.html', form=form)
    if request.method == 'POST' and form.validate_on_submit():
        form = VenueForm(request.form)
        venue = Venue(
            name = form.name.data,
            genres = form.genres.data,
            address = form.address.data,
            city = form.city.data,
            state = form.state.data,
            phone = form.phone.data,
            facebook_link = form.facebook_link.data,
        )
        try:
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash('Venue ' + form.name.data + ' was successfully listed!')
        except Exception as e:
            print(e)
            flash('An error occurred. Venue ' + form.name.data + ' could not be added.')
        finally:
            db.session.close()
        return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue_to_delete = Venue.query.filter_by(id=venue_id)
        venue_to_delete.delete()
    db.session.commit()
    except:
        db.session.rollback() 
    finally:
        db.session.close()

    return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    all_artists = Artist.query.all()
    data = []

    # Looping over each venue in the database
    for artist in all_artists:
        data.append({
        "id":artist.id,
        "name":artist.name
        })
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artist_select = Artist.query
    artist_list = []

    artists = artist_select.filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
    for artist in artists:
        artist_list.append({
        "id":artist.id,
        "name":artist.name,
        "num_upcoming_shows": 0,
        })

    response={
        "count": len(artist_list),
        "data": artist_list
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist_in_view = Artist.query.get(artist_id)
    data = {
        "id": artist_in_view.id,
        "name": artist_in_view.name,
        "genres": artist_in_view.genres,
        "city": artist_in_view.city,
        "state": artist_in_view.state,
        "phone": artist_in_view.phone,
        "seeking_venue": artist_in_view.seeking_venue,
        "image_link": artist_in_view.image_link,
        "facebook_link": artist_in_view.facebook_link
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_to_update = Artist.query.get(artist_id)
    artist = {
        "id": artist_to_update.id,
        "name": artist_to_update.name,
        "genres": artist_to_update.genres,
        "city": artist_to_update.city,
        "state": artist_to_update.state,
        "phone": artist_to_update.phone,
        "website": artist_to_update.website,
        "facebook_link": artist_to_update.facebook_link,
        "seeking_venue": artist_to_update.seeking_value,
        "seeking_description": artist_to_update.seeking_description,
        "image_link": artist_to_update.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.update(dict(request.get_json()))
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue_to_update = Venue.query.get(venue_id)
    venue = {
        "id": venue_to_update.id,
        "name": venue_to_update.name,
        "genres": venue_to_update.genres,
        "address": venue_to_update.city,
        "city": venue_to_update.state,
        "state": venue_to_update.phone,
        "phone": venue_to_update.website,
        "website": venue_to_update.facebook_link,
        "facebook_link": venue_to_update.seeking_value,
        "seeking_talent": venue_to_update.seeking_description,
        "image_link": venue_to_update.image_link
    }
    
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.update(request.to_json())
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
  artist = Artist(
    name = form.name.data,
    genres = form.genres.data,
    city = form.city.data,
    state = form.state.data,
    phone = form.phone.data,
    facebook_link = form.facebook_link.data
  )
  print(artist)
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    try:
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully listed!')
    except Exception as e:
        print(e)
        flash('An error occurred. Artist ' + form.name.data + ' could not be added.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    all_shows = Shows.query.join(Venue).join(Artist).all()
    for each_show in all_shows:
        data.append({
        "venue_id": each_show.venue_id,
        "venue_name": each_show.venue.name,
        "artist_id": each_show.artist_id,
        "artist_name": each_show.artist.name,
        "artist_image_link": each_show.artist.image_link,
        "start_time": each_show.start_time
        })
    
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)
    show = Shows(
        venue_id = form.venue_id.data,
        artist_id = form.artist_id.data,
        start_time = form.start_time.data
    )
    print(show)
    try:
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as e:
        print(e)
        flash('An error occurred. Show could not be added.')
    finally:
        db.session.close()
    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    


