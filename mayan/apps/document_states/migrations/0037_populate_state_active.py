from django.db import migrations


def code_populate_state_active(apps, schema_editor):
    WorkflowInstance = apps.get_model(
        app_label='document_states',
        model_name='WorkflowInstance'
    )

    def get_current_state(self):
        last_transition = self.get_last_transition()

        if last_transition:
            return last_transition.destination_state
        else:
            return self.workflow.get_state_initial()

    def get_last_log_entry(self):
        return self.log_entries.order_by('datetime').last()

    def get_last_transition(self):
        last_log_entry = self.get_last_log_entry()
        if last_log_entry:
            return last_log_entry.transition

    WorkflowInstance.get_current_state = get_current_state
    WorkflowInstance.get_last_log_entry = get_last_log_entry
    WorkflowInstance.get_last_transition = get_last_transition

    for workflow_instance in WorkflowInstance.objects.all():
        workflow_instance.state_active = workflow_instance.get_current_state()
        workflow_instance.save()


class Migration(migrations.Migration):
    dependencies = [
        ('document_states', '0036_workflowinstance_state_active')
    ]

    operations = [
        migrations.RunPython(
            code=code_populate_state_active,
            reverse_code=migrations.RunPython.noop
        )
    ]
