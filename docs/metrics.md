# Metrics

## average_price
Definition: mean(price)
Type: aggregation
Default aggregation: mean

## occupancy_proxy
Definition: (30 - availability_30) / 30
Type: derived_metric
Default aggregation: mean

## revenue_proxy
Definition: price * (30 - availability_30)
Type: derived_metric
Default aggregation: sum

## superhost_premium
Definition: mean(price | is_superhost=True) - mean(price | is_superhost=False)
Type: comparison

## review_activity
Definition: number_of_reviews or growth in number_of_reviews over time
Type: aggregation
Default aggregation: sum