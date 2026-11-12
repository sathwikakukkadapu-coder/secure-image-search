import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update initial currentThreshold to 0.20 instead of 0.50
text = text.replace('let currentThreshold = 0.50;', 'let currentThreshold = 0.20;')

# 2. In runContentFreeSearch:
# Update domain_filter in cfPayload to use detected_domain when currentDomainFilter is auto or empty,
# and set include_below_threshold: true so nearest neighbors are always retrieved.
old_payload = """        const cfPayload = {
          protected_vector: localData.protected_vector,
          top_k: currentTopK,
          threshold: currentThreshold,
          domain_filter: currentDomainFilter,
          strip_metadata: true,
          sigma: 0.05
        };"""

new_payload = """        const effectiveDomain = (currentDomainFilter && currentDomainFilter !== 'auto')
          ? currentDomainFilter
          : (localData.detected_domain || 'auto');

        const cfPayload = {
          protected_vector: localData.protected_vector,
          top_k: currentTopK,
          threshold: currentThreshold,
          domain_filter: effectiveDomain,
          include_below_threshold: true,
          strip_metadata: true,
          sigma: 0.05
        };"""

if old_payload in text:
    text = text.replace(old_payload, new_payload)
    print("Replaced cfPayload successfully!")
else:
    print("WARNING: old_payload not matched exactly, using regex...")
    text = re.sub(
        r'domain_filter:\s*currentDomainFilter,',
        r'domain_filter: (currentDomainFilter && currentDomainFilter !== "auto") ? currentDomainFilter : (localData.detected_domain || "auto"),\n          include_below_threshold: true,',
        text
    )

# 3. In loadSamplePreset:
old_sample_preset = """    async function loadSamplePreset(cat) {
      const urls = {
        medical: "/static/assets/medical_preset.jpg",
        biometrics: "/static/assets/biometric_preset.jpg",
        vehicles: "/static/assets/vehicle_bike.jpg",
        nature: "/static/assets/nature_preset.jpg"
      };"""

new_sample_preset = """    async function loadSamplePreset(cat) {
      const domainSelect = document.getElementById('domainFilterSelect');
      if (domainSelect) {
        domainSelect.value = cat;
        currentDomainFilter = cat;
      }
      const urls = {
        medical: "/static/assets/medical_preset.jpg",
        biometrics: "/static/assets/biometric_preset.jpg",
        vehicles: "/static/assets/vehicle_preset.jpg",
        nature: "/static/assets/nature_preset.jpg"
      };"""

if old_sample_preset in text:
    text = text.replace(old_sample_preset, new_sample_preset)
    print("Updated loadSamplePreset successfully!")
else:
    print("WARNING: old_sample_preset not matched exactly")

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated frontend/index.html with smart domain filtering & auto-retrieval!")
