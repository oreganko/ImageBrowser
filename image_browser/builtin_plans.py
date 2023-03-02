class BuiltinPlan:
    def __init__(self, name, thumbnail_sizes, show_original_link, create_expiring_link):
        self.name = name
        self.thumbnail_sizes = thumbnail_sizes
        self.show_original_link = show_original_link
        self.create_expiring_link = create_expiring_link


basic_plan = BuiltinPlan('Basic', ['200'], False, False)
premium_plan = BuiltinPlan('Premium', ['200', '400'], True, False)
enterprise_plan = BuiltinPlan('Enterprise', ['200', '400'], True, True)

builtin_thumbnail_sizes = {
    '200': {
        'height': 200,
        'width': 0
    },
    '400': {
        'height': 400,
        'width': 0
    }
}



