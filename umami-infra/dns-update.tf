# DNS record for analytics.ardotconsulting.com
# Add this to hetzner/dns.tf in the infra repo
# Points analytics.ardotconsulting.com to the lab server IP (167.233.115.58)

# Add this record to the existing dns.tf:
# resource "hetzner_dns_record" "umami_analytics" {
#   zone_id = data.hetzner_dns_zone.ardotconsulting_com.id
#   name    = "analytics"
#   value   = "167.233.115.58"
#   type    = "A"
#   ttl     = 3600
# }
