from google_play_scraper import reviews, Sort
from datetime import datetime, date
import time


class ReviewScraper:

    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2

    def scrape(
        self,
        package_id: str,
        from_date: date,
        to_date: date,
        rating: int = 0,
        hint: str = ""
    ):
        """
        Scrape reviews from Google Play Store with pagination.

        Multiple hints can be separated using |.

        Example:
            !! | @ | ; | ... | 👍
        """

        all_reviews = []
        continuation_token = None

        try:
            while True:

                try:
                    batch, continuation_token = reviews(
                        package_id,
                        lang="en",
                        country="in",
                        sort=Sort.NEWEST,
                        count=100,
                        continuation_token=continuation_token
                    )

                    if not batch:
                        break

                    last_review_date_obj = None

                    for review in batch:

                        # -----------------------------
                        # Parse review date
                        # -----------------------------
                        try:
                            review_timestamp = review.get("at")

                            if isinstance(review_timestamp, datetime):
                                review_datetime = review_timestamp
                                review_date_obj = review_datetime.date()

                            elif isinstance(review_timestamp, (int, float)):
                                review_datetime = datetime.fromtimestamp(
                                    review_timestamp / 1000.0
                                )
                                review_date_obj = review_datetime.date()

                            else:
                                continue

                        except Exception:
                            continue

                        last_review_date_obj = review_date_obj

                        # -----------------------------
                        # Date filter
                        # -----------------------------
                        if (
                            review_date_obj < from_date
                            or review_date_obj > to_date
                        ):
                            continue

                        # -----------------------------
                        # Rating filter
                        # -----------------------------
                        review_rating = review.get("score", 0)

                        if (
                            rating != 0
                            and review_rating != rating
                        ):
                            continue

                        # -----------------------------
                        # Hint filter
                        # -----------------------------
                        review_text = review.get("content", "")

                        if hint:
                            if not self._matches_hint(
                                review_text,
                                hint
                            ):
                                continue

                        # -----------------------------
                        # Format result
                        # -----------------------------
                        formatted_review = {
                            "User": review.get(
                                "userName",
                                "Unknown"
                            ),
                            "Review": review.get(
                                "content",
                                ""
                            ),
                            "Package ID": package_id,
                            "Rating": f"{review_rating}/5",
                            "Date": review_date_obj.strftime(
                                "%Y-%m-%d"
                            ),
                            "Time": review_datetime.strftime(
                                "%H:%M:%S"
                            )
                        }

                        all_reviews.append(formatted_review)

                    # -----------------------------
                    # Stop if older than date range
                    # -----------------------------
                    if (
                        last_review_date_obj
                        and last_review_date_obj < from_date
                    ):
                        break

                    # -----------------------------
                    # No more pages
                    # -----------------------------
                    if not continuation_token:
                        break

                    time.sleep(0.5)

                except Exception as e:
                    print(
                        f"Error fetching batch: {str(e)}"
                    )
                    break

            return all_reviews

        except Exception as e:
            print(f"Scraping error: {str(e)}")
            raise Exception(
                f"Failed to scrape reviews: {str(e)}"
            )

    def _matches_hint(
        self,
        review_text: str,
        hint: str
    ) -> bool:
        """
        Check if ANY supplied hint appears at the END
        of the review.

        Multiple hints must be separated using |.

        Example:
            !! | @ | ; | ... | 👍

        Text matching is case-insensitive.

        Emojis and symbols are matched exactly.

        Exact repeated-character count is enforced.

        Therefore:

            "This is good..."   -> MATCH
            "This is good...."  -> NO MATCH
        """

        if not hint:
            return True

        cleaned_review = review_text.rstrip()

        if not cleaned_review:
            return False

        # -----------------------------------------
        # Split multiple hints using |
        # -----------------------------------------
        hints = [
            h.strip()
            for h in hint.split("|")
            if h.strip()
        ]

        if not hints:
            return True

        # -----------------------------------------
        # Check every hint
        # -----------------------------------------
        for current_hint in hints:

            cleaned_hint = current_hint.rstrip()

            if not cleaned_hint:
                continue

            review_len = len(cleaned_review)
            hint_len = len(cleaned_hint)

            if review_len < hint_len:
                continue

            # -----------------------------------------
            # Determine Unicode / emoji / symbol
            # -----------------------------------------
            is_unicode = any(
                ord(char) > 127
                for char in cleaned_hint
            )

            # -----------------------------------------
            # Check ending
            # -----------------------------------------
            if is_unicode:
                ends = cleaned_review.endswith(
                    cleaned_hint
                )
            else:
                ends = cleaned_review.lower().endswith(
                    cleaned_hint.lower()
                )

            if not ends:
                continue

            # -----------------------------------------
            # Prevent repeated-character mismatch
            #
            # Example:
            #
            # Hint: ...
            #
            # Review: Good...   -> MATCH
            # Review: Good....  -> NO MATCH
            # -----------------------------------------
            start_idx = review_len - hint_len

            if start_idx > 0:

                preceding_char = cleaned_review[
                    start_idx - 1
                ]

                first_hint_char = cleaned_hint[0]

                if is_unicode:

                    if preceding_char == first_hint_char:
                        continue

                else:

                    if (
                        preceding_char.lower()
                        == first_hint_char.lower()
                    ):
                        continue

            # -----------------------------------------
            # A hint matched
            # -----------------------------------------
            return True

        # -----------------------------------------
        # No hint matched
        # -----------------------------------------
        return False
