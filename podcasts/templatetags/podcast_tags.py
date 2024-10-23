from django import template

register = template.Library()

@register.simple_tag
def build_tag_filter_url(tag_id:int, selected_tags:list=[]) -> str:
    """
        Builds a URL query string for the given tag, plus the currently selected tags.
    """
    tag_ids = [str(tag.id) for tag in selected_tags]
    tag_ids.append(str(tag_id))
    
    # Convert the unique list of tags IDs to a comma-separated string
    tag_ids_string = ','.join(set(tag_ids))
    
    return f"?tags={tag_ids_string}"
