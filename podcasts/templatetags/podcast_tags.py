from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag
def build_tag_filter_url(selected_tags, new_tag_id):
    """
    Builds a URL query string for selected tags and the new tag to be added.
    """
    # Convert the list of selected tags to a comma-separated string
    selected_tag_ids = ','.join(map(str, [tag.id for tag in selected_tags]))
    
    # Append the new tag ID to the selected tags
    if selected_tag_ids:
        tag_string = f"{selected_tag_ids},{new_tag_id}"
    else:
        tag_string = str(new_tag_id)
    
    # Return the URL with the updated query string
    return f"?tags={tag_string}"
