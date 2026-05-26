from app.models.project import Project, ProjectStatus
from app.repositories.project_repository import ProjectRepository

repo = ProjectRepository()


class ProjectService:
    def get_user_projects(self, user_id):
        return repo.get_all_for_user(user_id)

    def get_project(self, project_id):
        return repo.get_by_id(project_id)

    def create_project(self, user_id, form_data):
        project = Project(
            user_id=user_id,
            name=form_data['name'],
            client_name=form_data.get('client_name', ''),
            location=form_data.get('location', ''),
            zip_code=form_data.get('zip_code', ''),
            description=form_data.get('description', ''),
            status=ProjectStatus.ACTIVE,
        )
        return repo.save(project)

    def update_project(self, project, form_data):
        project.name = form_data['name']
        project.client_name = form_data.get('client_name', '')
        project.location = form_data.get('location', '')
        project.zip_code = form_data.get('zip_code', '')
        project.description = form_data.get('description', '')
        status_val = form_data.get('status', ProjectStatus.ACTIVE.value)
        project.status = ProjectStatus(status_val)
        return repo.save(project)

    def delete_project(self, project):
        repo.delete(project)

    def get_stats(self, user_id):
        projects = repo.get_all_for_user(user_id)
        active = [p for p in projects if p.status == ProjectStatus.ACTIVE]
        total_items = sum(
            len(item_list.items)
            for p in projects
            for item_list in p.material_lists
        )
        return {
            'total_projects': len(projects),
            'active_projects': len(active),
            'total_items': total_items,
        }
