terraform {
  required_version = ">= 1.10"

  backend "s3" {
    bucket       = "ardotconsulting-tfstate"
    key          = "umami/terraform.tfstate"
    region       = "us-west-2"
    use_lockfile = true
    encrypt      = true
  }

  required_providers {
    coolify = {
      source  = "coolify-terraform/coolify"
      version = "~> 0.1.29"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.13"
    }
  }
}

# Token from COOLIFY_TOKEN (.env.op).
provider "coolify" {
  endpoint = "https://coolify.ardotconsulting.com"
}

# Uses the gh CLI login (ryancheley) when GITHUB_TOKEN isn't set.
provider "github" {
  owner = "ardotconsulting"
}

locals {
  # The lab Coolify's own server (h-ac-web-p-001), created by the Coolify install.
  server_uuid = "jqrchg46aq85noy7ec9fsmx0"
}

# ---------------------------------------------------------------------------
# Umami analytics — self-hosted, privacy-first, open source (MIT)
# Blog post: "Self-Hosting Umami: Privacy-First Web Analytics Without Google Analytics"
# Deploys Umami + PostgreSQL via Coolify on the lab server.
# ---------------------------------------------------------------------------
locals {
  umami = {
    description = "Self-hosted Umami analytics — replaces Plausible Cloud"
    port        = "3000"
  }
}

resource "coolify_project" "umami" {
  name        = "umami"
  description = local.umami.description
}

resource "coolify_application" "umami" {
  name             = "umami"
  project_uuid     = coolify_project.umami.uuid
  server_uuid      = local.server_uuid
  environment_name = "production"
  git_repository   = "https://github.com/umami-software/umami"
  git_branch        = "master"
  build_pack        = "dockerfile"
  ports_exposes      = local.umami.port
  domains           = "https://analytics.ardotconsulting.com"
  # Same as the personal repo: the API doesn't return these on read.
  lifecycle {
    ignore_changes = [
      project_uuid,
      server_uuid,
      manual_webhook_secret_bitbucket,
      manual_webhook_secret_gitea,
      manual_webhook_secret_github,
      manual_webhook_secret_gitlab,
    ]
  }
}
