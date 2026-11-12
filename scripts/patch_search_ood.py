with open('backend/api/search.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    return {
        "status": "success",
        "content_free_mode": "ON",
        "domain_filter_applied": query.domain_filter or "all",
        "diagnostics": diagnostics,"""

replacement = """    top_candidate_sim = float(matches[0]["similarity"]) if matches else (float(below_matches[0]["similarity"]) if below_matches else 0.0)
    top_candidate_pct = f"{round(top_candidate_sim * 100.0, 1)}%"

    return {
        "status": "success",
        "content_free_mode": "ON",
        "domain_filter_applied": query.domain_filter or "all",
        "has_relevant_matches": len(matches) > 0,
        "is_out_of_domain": len(matches) == 0,
        "records_passed_threshold": len(matches),
        "records_rejected_threshold": len(below_matches),
        "top_similarity": round(top_candidate_sim, 4),
        "top_similarity_percent": top_candidate_pct,
        "diagnostics": diagnostics,"""

# Normalize line endings for replacement
if target in content:
    content = content.replace(target, replacement, 1)
    with open('backend/api/search.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully patched backend/api/search.py (LF)")
else:
    target_crlf = target.replace('\n', '\r\n')
    replacement_crlf = replacement.replace('\n', '\r\n')
    if target_crlf in content:
        content = content.replace(target_crlf, replacement_crlf, 1)
        with open('backend/api/search.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully patched backend/api/search.py (CRLF)")
    else:
        print("Target NOT FOUND in search.py")
