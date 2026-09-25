# Dataset Card — OULAD

## Source
Open University Learning Analytics Dataset (OULAD)  
Official access page: https://analyse.kmi.open.ac.uk/open_dataset  
Reference: Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2017). Open University Learning Analytics dataset. *Scientific Data*, 4, 170171. https://doi.org/10.1038/sdata.2017.171

## Scale and structure
The public release contains linked tables for courses, student information, registration, assessments and virtual-learning-environment activity. The published dataset contains 32,593 student registrations across 22 module presentations and more than ten million VLE interaction events.

## Tables used by this bundle
- `studentInfo.csv`: demographics, study background, module/presentation and final result;
- `studentRegistration.csv`: registration/unregistration timing;
- `assessments.csv`: module/presentation mapping for assessment identifiers;
- `studentAssessment.csv`: submission dates and scores.

Scores are **not** used in the default adjustment set or outcome.

## Privacy and governance
OULAD is anonymized, but educational records still deserve contextual care. Do not attempt re-identification or join student IDs to external sources.

## License
OULAD is publicly released for research; users should verify and follow the current terms on the official Open University page. Do not treat this repository as a substitute distributor of the raw dataset.

## Validity
The Open University context, distance-learning design, module structure and historical period constrain transfer. A module-presentation cohort is not representative of all higher-education learners.
