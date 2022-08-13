import enum


class GQLQueries(str, enum.Enum):
    FRUITS_DATALOADERS = """{
        fruits {
            name
            plant {
                name
            }
            color {
                name
            }
            eaters {
                name
            }
        }
    }"""
