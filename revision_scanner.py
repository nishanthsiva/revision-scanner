#!/usr/bin/env python3

from subprocess import PIPE,Popen,\
check_output,DEVNULL,call,CalledProcessError,\
TimeoutExpired

import os

def getBenchmarkFolders(benchmark_path):
        benchmarks = []
        for root,dir,files in os.walk(benchmark_path):
            for item in dir:
                benchmarks.append(root+item)
            break
        return benchmarks

def get_files_by_type(benchmark,file_type):
        result_files = []
        for root,dir,files in os.walk(benchmark):
            for f in files:
                if f.endswith(file_type):
                    result_files.append(root+'/'+f)
        return result_files

def get_version_update_lines(revision_string):
    revision_lines = revision_string.split('\n')
    version_lines = ''
    num_lines = 0
    for i in range(0,len(revision_lines)):
        line = revision_lines[i]
        if line.startswith('-') and '<version>' in line and '</version>' in line:
            next_line = revision_lines[i+1]
            if next_line.startswith('+') and '<version>' in next_line and '</version>' in next_line:
                version_lines += line+'\n'+next_line+'\n'
                num_lines += 1
    return num_lines,version_lines

def scan_revisions(benchmark_folder):
    f_log = open('revision_scanner_log.log','w')
    benchmarks = getBenchmarkFolders(benchmark_folder)
    break_flag = False
    files_scanned = 0
    changes_found = 0
    sum_change_lines = 0
    for benchmark in benchmarks:
        pom_files = get_files_by_type(benchmark,'pom.xml')
        print(''+str(len(pom_files)))
        files_scanned += len(pom_files)
        for pom_file in pom_files:
            command = 'cd '+benchmark+';'
            command += 'git log --follow -p -- '+pom_file
            try:
                print('Running cmd - '+command)
                p = Popen(command,shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                response,_ = p.communicate(input=None, timeout=300)
                response = response.decode('utf8')
                num_lines,version_lines = get_version_update_lines(response)
                if num_lines != 0:
                    changes_found += 1
                    if num_lines < 50:
                        sum_change_lines += num_lines
                    f_log.write(str(num_lines)+' version changes!\n')
                    f_log.write(version_lines+'\n\n')
            except (Exception) as e:
                p.kill()
                f_log.write(str(e)+'\n')
    f_log.write('Files Scanned = '+str(files_scanned)+'\n')
    f_log.write('Changes Found = '+str(changes_found)+'\n')
    f_log.write('Average Changes per file = '+str(sum_change_lines/changes_found))
    f_log.close()



def main():
    scan_revisions('/Users/nishanthsivakumar/Documents/libcompat/project_repo/maven_projects/')

if __name__ == '__main__':
    main()
