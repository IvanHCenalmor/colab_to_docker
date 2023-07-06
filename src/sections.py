
def calculate_next_section(current_section):
    current_section_parts = current_section.split('.')
    next_section_parts = current_section_parts.copy()
    next_section_parts[-2] = str(int(next_section_parts[-2]) + 1)
    next_section = '.'.join(next_section_parts)
    return next_section

def find_matching_prefix(string1, string2):
    matching_prefix = ""
    for i in range(min(len(string1), len(string2))):
        if string1[i] == string2[i]:
            matching_prefix += string1[i]
        else:
            break
    return matching_prefix

def update_cell_sections(cells, section_localizer, section_to_rmv, next_section):
    updated_cells = cells.copy()
    updated_section_localizer = section_localizer.copy()

    num_removed_cells = section_localizer[next_section] - section_localizer[section_to_rmv]
    matching_section = find_matching_prefix(section_to_rmv, next_section)

    for section in section_localizer:
        if section.startswith(section_to_rmv):
            updated_section_localizer.pop(section)
    
    since_section = next_section.replace(matching_section, '', 1)
    since_section_part = since_section.split('.')
    for section in section_localizer:
        if section.startswith(matching_section):
            acual_section = section.replace(matching_section, '', 1)
            acual_section_part = acual_section.split('.')
            if acual_section_part[0] >= since_section_part[0]:
                cell_id = updated_section_localizer.pop(section)
                updated_section = matching_section + '.'.join([str(int(acual_section_part[0])-1)] + acual_section_part[1:])
                updated_section_localizer[updated_section] = cell_id - num_removed_cells
                updated_cells[cell_id - num_removed_cells].source = updated_cells[cell_id - num_removed_cells].source.replace(section, updated_section, 1)


    return updated_cells, updated_section_localizer

def remove_section(cells, section_localizer, section_to_rmv):
    cell_idx_to_rmv = section_localizer[section_to_rmv]
    next_section = calculate_next_section(section_to_rmv)

    while next_section not in section_localizer:
        new_next_section = '.'.join(next_section.split('.')[:-2]) + '.'
        if new_next_section == '.':
            next_section = section_to_rmv
        next_section = calculate_next_section(new_next_section)
        
    next_section_cell_idx = section_localizer[next_section]

    reduced_cells = cells[:cell_idx_to_rmv] + cells[next_section_cell_idx:]

    updated_cells, updated_section_localizer = update_cell_sections(reduced_cells, section_localizer, 
                                                                    section_to_rmv, next_section)
    return updated_cells, updated_section_localizer

def remove_section_list(cells, section_localizer, section_list):

    sorted_sections = sorted(section_list, key=lambda x: [int(num) for num in x.split('.')[:-1]], reverse=True)
    for section in sorted_sections:
        cells, section_localizer = remove_section(cells.copy(), section_localizer.copy(), section)

    return cells, section_localizer 