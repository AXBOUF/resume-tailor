#!/bin/bash
# Docker helper script for Resume Tailor
# Makes it easy to run tools in Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker and Docker Compose found"
}

# Build the Docker image
build() {
    print_info "Building Resume Tailor Docker image..."
    docker-compose build
    print_success "Docker image built successfully"
}

# Parse resume
parse_resume() {
    if [ -z "$1" ]; then
        print_error "Please provide a resume file"
        echo "Usage: ./docker-run.sh parse <resume.pdf|docx>"
        exit 1
    fi
    
    local resume_file="$1"
    if [ ! -f "$resume_file" ]; then
        print_error "File not found: $resume_file"
        exit 1
    fi
    
    print_info "Parsing resume: $resume_file"
    docker-compose run --rm tailor python3 parse_resume.py "$resume_file"
    print_success "Resume parsed successfully"
}

# Scrape jobs
scrape_jobs() {
    if [ -z "$1" ]; then
        print_error "Please provide job URL(s)"
        echo "Usage: ./docker-run.sh scrape <url1> [url2] [url3] ..."
        exit 1
    fi
    
    print_info "Scraping job(s)..."
    docker-compose run --rm tailor python3 scrape_jobs_v2.py "$@"
    print_success "Jobs scraped successfully"
}

# Generate tailored resumes
tailor_resume() {
    local resume_json="${1:-resume_parsed.json}"
    local jobs_json="${2:-jobs_scraped_v2.json}"
    local output_dir="${3:-./output}"
    
    if [ ! -f "$resume_json" ]; then
        print_error "Resume JSON not found: $resume_json"
        echo "Run './docker-run.sh parse <resume.pdf>' first"
        exit 1
    fi
    
    if [ ! -f "$jobs_json" ]; then
        print_error "Jobs JSON not found: $jobs_json"
        echo "Run './docker-run.sh scrape <job_url>' first"
        exit 1
    fi
    
    print_info "Generating tailored resumes..."
    print_info "Resume: $resume_json"
    print_info "Jobs: $jobs_json"
    print_info "Output: $output_dir"
    
    docker-compose run --rm tailor python3 tailor_resume_latex.py "$resume_json" "$jobs_json" "$output_dir"
    print_success "Tailored resumes generated successfully"
}

# Compile LaTeX to PDF using Docker
compile_pdf() {
    local tex_file="$1"
    
    if [ -z "$tex_file" ]; then
        # Compile all .tex files in output directory
        print_info "Compiling all .tex files in output/ directory..."
        
        for tex in output/*.tex; do
            if [ -f "$tex" ]; then
                local basename=$(basename "$tex" .tex)
                print_info "Compiling: $basename.tex"
                
                # Run pdflatex twice for references
                docker-compose run --rm latex -interaction=nonstopmode "$basename.tex" || true
                docker-compose run --rm latex -interaction=nonstopmode "$basename.tex" || true
            fi
        done
        
        print_success "PDF compilation complete"
        ls -lh output/*.pdf 2>/dev/null || print_error "No PDF files found"
    else
        if [ ! -f "$tex_file" ]; then
            print_error "File not found: $tex_file"
            exit 1
        fi
        
        local basename=$(basename "$tex_file" .tex)
        local dir=$(dirname "$tex_file")
        
        print_info "Compiling: $tex_file"
        
        # Run pdflatex twice
        docker-compose run --rm -w "/workdir/$dir" latex -interaction=nonstopmode "$basename.tex" || true
        docker-compose run --rm -w "/workdir/$dir" latex -interaction=nonstopmode "$basename.tex" || true
        
        print_success "PDF created: ${tex_file%.tex}.pdf"
    fi
}

# Interactive mode
interactive() {
    print_info "Starting interactive shell in Docker container..."
    docker-compose run --rm tailor bash
}

# Full workflow
full_workflow() {
    local resume_file="$1"
    shift
    local job_urls=("$@")
    
    if [ -z "$resume_file" ] || [ ${#job_urls[@]} -eq 0 ]; then
        print_error "Usage: ./docker-run.sh full <resume.pdf> <job_url1> [job_url2] ..."
        exit 1
    fi
    
    print_info "🚀 Starting full workflow..."
    
    # Step 1: Parse resume
    parse_resume "$resume_file"
    
    # Step 2: Scrape jobs
    scrape_jobs "${job_urls[@]}"
    
    # Step 3: Generate tailored resumes
    tailor_resume "resume_parsed.json" "jobs_scraped_v2.json" "./output"
    
    # Step 4: Compile PDFs
    compile_pdf
    
    print_success "🎉 Full workflow complete! Check output/ directory"
}

# Show help
show_help() {
    cat << EOF
Resume Tailor - Docker Helper Script

Usage: ./docker-run.sh [COMMAND] [OPTIONS]

Commands:
    build                   Build Docker image
    parse <file>            Parse PDF/DOCX resume
    scrape <url> [url...]   Scrape job URLs
    tailor [resume] [jobs] [output]  Generate tailored resumes
    compile [file]          Compile LaTeX to PDF
    interactive             Start interactive shell
    full <resume> <urls...> Run complete workflow
    help                    Show this help message

Examples:
    # Build Docker image
    ./docker-run.sh build

    # Parse resume
    ./docker-run.sh parse my_resume.pdf

    # Scrape single job
    ./docker-run.sh scrape "https://jobs.lever.co/company/job"

    # Scrape multiple jobs
    ./docker-run.sh scrape "url1" "url2" "url3"

    # Generate tailored resumes (uses default filenames)
    ./docker-run.sh tailor

    # Generate with custom files
    ./docker-run.sh tailor my_resume.json my_jobs.json ./my_output

    # Compile all .tex files in output/
    ./docker-run.sh compile

    # Compile specific file
    ./docker-run.sh compile output/Mun_Albaraili_Data_Engineer_Talenza.tex

    # Full workflow (parse + scrape + tailor + compile)
    ./docker-run.sh full my_resume.pdf "https://jobs.lever.co/company1/job" "https://jobs.lever.co/company2/job"

Prerequisites:
    - Docker installed
    - Docker Compose installed
    - .env file with GROQ_API_KEY

EOF
}

# Main
main() {
    case "${1:-help}" in
        build)
            check_docker
            build
            ;;
        parse)
            shift
            check_docker
            parse_resume "$@"
            ;;
        scrape)
            shift
            check_docker
            scrape_jobs "$@"
            ;;
        tailor)
            shift
            check_docker
            tailor_resume "$@"
            ;;
        compile)
            shift
            check_docker
            compile_pdf "$@"
            ;;
        interactive)
            check_docker
            interactive
            ;;
        full)
            shift
            check_docker
            full_workflow "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"