from test_registries import awesome_people

@awesome_people.register
class AlainDamasio:
    pass

print("imported", awesome_people)