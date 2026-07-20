provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

resource "aws_eks_cluster" "atlas_cluster" {
  name     = "atlas-data-control-cluster"
  role_arn = aws_iam_role.eks_role.arn

  vpc_config {
    subnet_ids = var.subnet_ids
  }
}

resource "aws_iam_role" "eks_role" {
  name = "atlas-eks-cluster-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "eks.amazonaws.com" }
    }]
  })
}
