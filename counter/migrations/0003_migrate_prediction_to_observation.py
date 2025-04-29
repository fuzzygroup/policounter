from django.db import migrations


def move_prediction_data(apps, schema_editor):
    Observation = apps.get_model('counter', 'Observation')
    Prediction = apps.get_model('counter', 'Prediction')
    db_alias = schema_editor.connection.alias

    for obs in Observation.objects.using(db_alias).all():
        try:
            # manually resolve Prediction via assumed 1-to-1 relationship, fallback if it doesn't exist
            pred = Prediction.objects.using(db_alias).get(id=obs.id)
        except Prediction.DoesNotExist:
            continue

        obs.input_image = pred.input_image
        obs.density_map = pred.density_map
        obs.model_name = pred.model_name
        obs.weight_selection = pred.weight_selection
        obs.save()



class Migration(migrations.Migration):

    dependencies = [
        ("counter", "0002_alter_observation_options_and_more"),
    ]

    operations = [
        migrations.RunPython(move_prediction_data),
    ]

