from .intersect_lib import class_merger
from .untyped_lib import NumberLike

NewNumberLike = class_merger("NewNumberLike", NumberLike)
new_num = NewNumberLike(5)  # Unknown init
new_num.multiplier()  # Unknown
new_num.randomiser()  # Ideally this is known?
