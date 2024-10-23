from django import template

register = template.Library()

@register.simple_tag
def build_tag_filter_url(tag_id:int, selected_tags:list=None) -> str:
    """Builds a URL query string for the given tag, plus the currently selected tags."""
    
    # Instead of creating the empty list as a default parameter,
    # the default is None to avoid odd behaviour with default mutables
    if selected_tags is None:
        selected_tags = []
    
    # Assemble list of the given tag's ids as ints
    tag_ids = [int(tag.id) for tag in selected_tags if hasattr(tag, 'id')]
    tag_ids.append(int(tag_id))
    
    # Remove duplicates and sort numerically
    tag_ids = list(set(tag_ids))
    tag_ids.sort(key=int)
    
    # Convert the list of tags IDs to a comma-separated string
    tag_ids_string = ','.join(map(str, tag_ids))
    
    return f"?tags={tag_ids_string}"
