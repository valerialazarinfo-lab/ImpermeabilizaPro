/* Estimativas preliminares. Valores sujeitos a validação técnica. */
export function estimate(input, config) {
  const area = Number(input.area);
  if (!Number.isFinite(area) || area <= 0 || area > 10000) return {review:true, reason:"Área inválida ou desconhecida"};
  if (input.complex || input.difficultAccess || input.unknownSubstrate) return {review:true, reason:"É necessária avaliação técnica"};
  const band = config.price_bands_eur_per_m2_ex_vat[input.service];
  if (!band) return {review:true, reason:"Serviço sujeito a avaliação técnica"};
  const min = Math.max(config.minimum_complete_project_ex_vat, area * band.min);
  const max = Math.max(min, area * band.max);
  return {review:false, min:Math.ceil(min/10)*10, max:Math.ceil(max/10)*10, currency:"EUR", vatIncluded:false, provisional:true};
}
