# Dataset Schema – Copenhagen Airbnb

## listing_id
Unique identifier for listing.

## city
City of listing (constant: copenhagen).

## neighbourhood
Cleaned Airbnb neighbourhood name.

## room_type
Type of listing:
- Entire home/apt
- Private room
- Shared room

## price
Nightly listing price in DKK.

## availability_30
Number of days the listing is available in the next 30 days.

## number_of_reviews
Total number of reviews the listing has received.

## review_score
Overall review rating (0–5 scale). Missing if no reviews.

## last_review
Date of most recent review.

## minimum_nights
Minimum stay requirement in nights.

## is_superhost
Boolean indicating whether the host is a superhost.