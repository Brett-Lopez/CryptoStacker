#container repository
#https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecr_repository

resource "aws_ecr_repository" "csr-flask-web-app-tf" {
  name                 = "csr-flask-web-app-tf"
  image_tag_mutability = "MUTABLE"

  encryption_configuration {
  encryption_type = "AES256"
  }

  image_scanning_configuration {
    scan_on_push = true
  }

}

#aws_ecr_lifecycle_policy
resource "aws_ecr_lifecycle_policy" "csr-flask-web-app-lf-cy-tf" {
  repository = aws_ecr_repository.csr-flask-web-app-tf.name

  policy = <<EOF
{
    "rules": [
        {
            "rulePriority": 1,
            "description": "Keep last 30 images",
            "selection": {
                "tagStatus": "untagged",
                "countType": "imageCountMoreThan",
                "countNumber": 10
            },
            "action": {
                "type": "expire"
            }
        },
        {
            "rulePriority": 2,
            "description": "Keep last 30 images",
            "selection": {
                "tagStatus": "tagged",
                "tagPrefixList": ["CSR", "CSR-flask-web-app-tf"],
                "countType": "imageCountMoreThan",
                "countNumber": 10
            },
            "action": {
                "type": "expire"
            }
        }
    ]
}
EOF
}
