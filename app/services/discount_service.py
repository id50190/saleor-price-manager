from typing import List, Dict, Optional
import json
from datetime import datetime
import pytz
from croniter import croniter
from decimal import Decimal

class DiscountService:
    """Service for managing product discounts with cron scheduling"""
    
    @staticmethod
    def parse_discounts(discounts_json: str) -> List[Dict]:
        """Parse discounts JSON string to list of discount objects"""
        try:
            return json.loads(discounts_json) if discounts_json else []
        except json.JSONDecodeError:
            return []
    
    @staticmethod
    def format_discounts(discounts: List[Dict]) -> str:
        """Format discounts list to JSON string"""
        return json.dumps(discounts, ensure_ascii=False)
    
    def get_active_discount(self, discounts: List[Dict], current_time: datetime = None) -> Optional[Dict]:
        """Get the first active discount based on period and cron schedule"""
        if not discounts:
            return None
            
        if current_time is None:
            current_time = datetime.now(pytz.UTC)
        
        for discount in discounts:
            if self._is_discount_active(discount, current_time):
                return discount
        
        return None
    
    def _is_discount_active(self, discount: Dict, current_time: datetime) -> bool:
        """Check if discount is active based on period and cron schedule"""
        # Check period
        if not self._is_within_period(discount, current_time):
            return False
        
        # Check cron schedule
        return self._is_cron_active(discount, current_time)
    
    def _is_within_period(self, discount: Dict, current_time: datetime) -> bool:
        """Check if current time is within discount period"""
        period = discount.get("period", {})
        
        # If no period specified, discount is always valid by period
        if not period:
            return True
        
        start_str = period.get("datetime_start")
        end_str = period.get("datetime_end")
        
        if not start_str or not end_str:
            return True
        
        try:
            # Parse dates - format: DD-MM-YYYYTHH:MM:SSZ
            start_date = datetime.strptime(start_str, "%d-%m-%YT%H:%M:%SZ")
            end_date = datetime.strptime(end_str, "%d-%m-%YT%H:%M:%SZ")
            
            # Make timezone aware
            start_date = pytz.UTC.localize(start_date) if start_date.tzinfo is None else start_date
            end_date = pytz.UTC.localize(end_date) if end_date.tzinfo is None else end_date
            
            return start_date <= current_time <= end_date
            
        except (ValueError, TypeError) as e:
            print(f"Error parsing discount period: {e}")
            return False
    
    def _is_cron_active(self, discount: Dict, current_time: datetime) -> bool:
        """Check if current time matches cron schedule"""
        schedule = discount.get("shedule", "* * * * *")  # Default: always active
        
        try:
            # Create croniter instance
            cron = croniter(schedule, current_time)
            
            # Check if current time matches the cron expression
            # We check if the current minute matches the cron schedule
            current_minute = current_time.replace(second=0, microsecond=0)
            next_run = cron.get_next(datetime)
            prev_run = cron.get_prev(datetime)
            
            # If current time is within the same minute as a scheduled run, it's active
            return (abs((current_minute - prev_run).total_seconds()) < 60 or
                   abs((current_minute - next_run).total_seconds()) < 60)
            
        except (ValueError, TypeError) as e:
            print(f"Error parsing cron schedule '{schedule}': {e}")
            # If cron parsing fails, default to active
            return True
    
    def apply_discount(self, base_price: Decimal, discount: Dict) -> Decimal:
        """Apply discount to base price with cap consideration"""
        if not discount:
            return base_price
        
        percent = Decimal(str(discount.get("percent", 0)))
        cap = Decimal(str(discount.get("cap", "0")))
        
        # Apply percentage discount/markup
        discount_factor = Decimal("1") + (percent / Decimal("100"))
        discounted_price = base_price * discount_factor
        
        # Apply cap (maximum/minimum price limit)
        if cap > 0:
            if percent > 0:  # Markup - cap is maximum
                discounted_price = min(discounted_price, cap)
            elif percent < 0:  # Discount - cap is minimum
                discounted_price = max(discounted_price, cap)
        
        return discounted_price.quantize(Decimal('0.01'))
    
    def validate_discount(self, discount: Dict) -> List[str]:
        """Validate discount data structure"""
        errors = []
        
        # Check required fields
        if "percent" not in discount:
            errors.append("Missing 'percent' field")
        else:
            try:
                float(discount["percent"])
            except (ValueError, TypeError):
                errors.append("'percent' must be a number")
        
        if "cap" not in discount:
            errors.append("Missing 'cap' field")
        else:
            try:
                float(discount["cap"])
            except (ValueError, TypeError):
                errors.append("'cap' must be a number")
        
        # Validate cron schedule
        schedule = discount.get("shedule", "* * * * *")
        try:
            croniter(schedule)
        except (ValueError, TypeError):
            errors.append(f"Invalid cron schedule: {schedule}")
        
        # Validate period if present
        period = discount.get("period")
        if period:
            start_str = period.get("datetime_start")
            end_str = period.get("datetime_end")
            
            if start_str:
                try:
                    datetime.strptime(start_str, "%d-%m-%YT%H:%M:%SZ")
                except ValueError:
                    errors.append(f"Invalid datetime_start format: {start_str}")
            
            if end_str:
                try:
                    datetime.strptime(end_str, "%d-%m-%YT%H:%M:%SZ")
                except ValueError:
                    errors.append(f"Invalid datetime_end format: {end_str}")
        
        return errors

# Global instance
discount_service = DiscountService()
