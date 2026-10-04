import os
from flask import Flask, request, render_template, redirect, session
from lib.database_connection import get_flask_database_connection, DatabaseConnection
from lib.user import User
from lib.user_repository import UserRepository
from lib.listing_repository import ListingRepository
from lib.listing import Listing
from lib.booking_request_repo import BookingRequestRepository
from lib.booking_request import BookingRequest
from lib.confirmed_booking_repo import ConfirmedBookingRepository
from lib.confirmed_booking import ConfirmedBooking
from flask_bcrypt import Bcrypt
from login_required import login_required_decorator
from datetime import date

# Create a new Flask app
app = Flask(__name__)
app.secret_key = "jay_is_very_cool"
bcrypt = Bcrypt(app)
UPLOAD_FOLDER = "static/images"

# == Your Routes Here ==


# GET /index
# Returns the homepage
# Try it:
#   ; open http://localhost:5001/


# --- HOMEPAGE ---
@app.route("/", methods=["GET"])
def get_index():
    connection = get_flask_database_connection(app)
    listing_repository = ListingRepository(connection)
    listings = listing_repository.all()

    try:
        user_id = session["user_id"]
    except KeyError:
        user_id = None

    return render_template("index.html", listings=listings, user_id=user_id)


# ----------------
# --- BOOKING REQUEST PAGE(S) ---
@app.route("/listings/<listing_id>")
def get_individual_listing(listing_id):
    db_conn = get_flask_database_connection(app)
    listing_repo = ListingRepository(db_conn)
    listing = listing_repo.find(listing_id)
    today = date.today().isoformat()

    return render_template("listing_page.html", listing=listing, today=today)


@app.route("/listings/<listing_id>", methods=["POST"])
@login_required_decorator
def request_booking(listing_id):
    db_conn = get_flask_database_connection(app)
    booking_request_repo = BookingRequestRepository(db_conn)
    listing_repo = ListingRepository(db_conn)
    confirmed_booking_repo = ConfirmedBookingRepository(db_conn)

    listing_object = listing_repo.find(listing_id)

    booking_request_details = request.form
    # Form date is a string, need to compare it against datetime.date from database.
    requested_date = date.fromisoformat(booking_request_details["date"])

    if (
        requested_date < listing_object.start_date
        or requested_date > listing_object.end_date
    ):
        return redirect("/booking_request/failed")

    # look in booking repo for booking on same date and listing
    existing_booking = confirmed_booking_repo.get_by_listing_id_and_date(
        listing_id, requested_date
    )
    if existing_booking is not None:
        return redirect("/booking_request/failed")

    booking_request = BookingRequest(
        listing_id=listing_id,
        guest_id=session["user_id"],
        date=booking_request_details["date"],
    )
    booking_request_repo.create(booking_request)

    return redirect("/")


@app.route("/booking_requests", methods=["GET"])
@login_required_decorator
def get_requests_for_owner():
    db_conn = get_flask_database_connection(app)
    booking_request_repo = BookingRequestRepository(db_conn)
    listing_repo = ListingRepository(db_conn)
    user_repo = UserRepository(db_conn)

    booking_requests = booking_request_repo.get_by_owner_id(session["user_id"])

    # for each booking request get guest user details from user repo, listing details from listing repo
    # create a new list of tuples (booking_request, listing_details, guest_user_details)
    booking_request_details = []
    for booking_request in booking_requests:
        listing = listing_repo.find(booking_request.listing_id)
        guest_user = user_repo.find_by_id(booking_request.guest_id)
        booking_request_details.append(
            (
                listing.name,
                guest_user.username,
                booking_request.date,
                booking_request.id,
            )
        )

    return render_template(
        "booking_requests.html", booking_request_details=booking_request_details
    )


@app.route("/booking_requests/<booking_request_id>/accept", methods=["POST"])
@login_required_decorator
def accept_booking_request(booking_request_id):
    db_conn = get_flask_database_connection(app)
    booking_request_repo = BookingRequestRepository(db_conn)
    confirmed_booking_repo = ConfirmedBookingRepository(db_conn)
    booking_request_details = booking_request_repo.get_by_id(booking_request_id)
    confirmed_booking = ConfirmedBooking(
        listing_id=booking_request_details.listing_id,
        guest_id=booking_request_details.guest_id,
        date=booking_request_details.date,
    )
    confirmed_booking_repo.create(confirmed_booking)
    booking_request_repo.delete(booking_request_id)
    return redirect("/booking_requests")


@app.route("/booking_requests/<booking_request_id>/decline", methods=["POST"])
@login_required_decorator
def decline_booking_request(booking_request_id):
    db_conn = get_flask_database_connection(app)
    booking_request_repo = BookingRequestRepository(db_conn)

    booking_request_repo.delete(booking_request_id)

    return redirect("/booking_requests")


@app.route("/confirmed_guest_bookings", methods=["GET"])
@login_required_decorator
def see_my_bookings_as_guest():
    db_conn = get_flask_database_connection(app)
    confirmed_booking_repo = ConfirmedBookingRepository(db_conn)
    listing_repo = ListingRepository(db_conn)
    confirmed_bookings = confirmed_booking_repo.get_by_guest_id(session["user_id"])
    confirmed_bookings_details = []
    for confirmed_booking in confirmed_bookings:
        listing = listing_repo.find(confirmed_booking.listing_id)
        confirmed_bookings_details.append((listing.name, confirmed_booking.date))
    return render_template(
        "confirmed_guest_bookings.html",
        confirmed_bookings_details=confirmed_bookings_details,
    )


# ----------------------------------
# --- LOGIN PAGE ---
@app.route("/sessions/new", methods=["GET"])
def get_login_form():
    return render_template("login_form.html")


@app.route("/sessions", methods=["POST"])
def create_session():
    form_data = request.form
    # print(form_data)
    connection = get_flask_database_connection(app)
    user_repo = UserRepository(connection)
    user_object = user_repo.find_by_email(form_data.get("email"))
    if user_object is None:
        return redirect("/sessions/failed")

    is_password_correct = user_repo.check_password_matches(
        user_object, form_data.get("password")
    )

    # print(f">>> PASSWORD MATCHES: {is_password_correct}")

    if is_password_correct:
        session["user_id"] = user_object.id
        return redirect("/")

    else:
        return redirect("/sessions/failed")


# -----------------------
# --- CREATE LISTING PAGE ---
@app.route("/listings", methods=["GET"])
def get_listings():
    today = date.today().isoformat()
    return render_template("listings.html", today=today)


@app.route("/listings", methods=["POST"])
@login_required_decorator
def create_listing():
    connection = get_flask_database_connection(app)
    listing_repository = ListingRepository(connection)

    listing_details = request.form
    
    file = request.files["image_upload"]

    file_extension = file.filename.split(".")[-1]
    try:
        file.save(f"static/images/{session['user_id']}_{listing_details['name']}.{file_extension}")
    except:
        # Uploading file during test doesn't work as it's readonly filesystem.
        pass

    if listing_details["end_date"] < listing_details["start_date"]:
        return redirect("/listings/failed")

    listing = Listing(
        owner_id=session["user_id"],
        name=listing_details["name"],
        description=listing_details["description"],
        price_per_night=listing_details["price_per_night"],
        start_date=listing_details["start_date"],
        end_date=listing_details["end_date"],
        image_path=f"{session['user_id']}_{listing_details['name']}.{file_extension}",
    )
    listing_repository.create(listing)

    return redirect("/")


# ------------------------------
# --- SIGN UP PAGE ---
@app.route("/sign-up", methods=["GET"])
def signup_form():
    return render_template("signup_form.html")


@app.route("/sign-up", methods=["POST"])
def create_user():
    signup_form_data = request.form
    connection = get_flask_database_connection(app)
    user_repo = UserRepository(connection)
    new_user = user_repo.create(signup_form_data)
    if new_user == False:
        return redirect("/sign-up/failed")
    return redirect("/")


# ---------------------
# --- FAIL PAGES ---
@app.route("/sign-up/failed", methods=["GET"])
def signup_form_fail():
    return render_template("signup_form_fail.html")


@app.route("/sessions/failed", methods=["GET"])
def login_form_fail():
    return render_template("login_form_fail.html")


@app.route("/listings/failed", methods=["GET"])
@login_required_decorator
def create_listing_fail():
    return render_template("listings_fail.html")


@app.route("/booking_request/failed", methods=["GET"])
@login_required_decorator
def create_booking_request_fail():
    return render_template("booking_request_fail.html")


# ------------------
# --- LOGOUT ---
@app.route("/logout", methods=["GET"])
@login_required_decorator
def logout():
    session["user_id"] = None
    return redirect("/")


# ------------------

# These lines start the server if you run this file directly
# They also start the server configured to use the test database
# if started in test mode.
if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5001)))
