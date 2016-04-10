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
    commit_line = ''
    for i in range(0,len(revision_lines)):
        line = revision_lines[i]
        if line.startswith('commit'):
            commit_line = line
        if line.startswith('-') and '<version>' in line and '</version>' in line:
            next_line = revision_lines[i+1]
            if next_line.startswith('+') and '<version>' in next_line and '</version>' in next_line:
                version_lines +=commit_line+'\n'+line+'\n'+next_line+'\n'
                num_lines += 1
    return num_lines,version_lines

def get_commit_lines(lines):
    commit_lines = ''
    num_commits = 0
    for line in lines.split('\n'):
        if line.startswith('commit'):
            num_commits += 1
            commit_lines +=line+'\n'
    return num_commits,commit_lines

def get_commit_history():
    f_commit_log = open('revision_commit_log.log','r')
    f_commit_history_log = open('commit_history.log','w')
    commit_lines = f_commit_log.readlines()
    command = ''
    for line in commit_lines:
        if line.startswith('Benchmark-'):
            folder_path = line.split('Benchmark-')[1]
            benchmark = folder_path.split('\n')[0]
            command = 'cd '+benchmark+';'
            f_commit_history_log.write('\n\n**********************************\n')
            f_commit_history_log.write('Scanning Benchmark - '+benchmark+'\n')
        if line.startswith('commit'):
            revision_id = line.split('commit ')[1]
            command += 'git show '+revision_id
            try:
                print('Running cmd - '+command)
                p = Popen(command,shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                response,_ = p.communicate(input=None, timeout=300)
                response = response.decode('utf8')
                f_commit_history_log.write('Analyzing Commit - '+revision_id+'\n')
                f_commit_history_log.write(response)
                f_commit_history_log.write('\n\n')
                command = ''
            except (Exception) as e:
                p.kill()
                print(str(e))
    f_commit_log.close()
    f_commit_history_log.close()

def scan_revisions(benchmark_folder):
    f_log = open('revision_scanner_log.log','w')
    f_commit_log = open('revision_commit_log.log','w')
    benchmarks = getBenchmarkFolders(benchmark_folder)
    break_flag = False
    files_scanned = 0
    changes_found = 0
    sum_change_lines = 0
    for benchmark in benchmarks:
        pom_files = get_files_by_type(benchmark,'pom.xml')
        #print(''+str(len(pom_files)))
        files_scanned += len(pom_files)
        for pom_file in pom_files:
            command = 'cd '+benchmark+';'
            command += 'git log --follow -p -- '+pom_file
            try:
                #print('Running cmd - '+command)
                p = Popen(command,shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                response,_ = p.communicate(input=None, timeout=300)
                response = response.decode('utf8')
                num_lines,version_lines = get_version_update_lines(response)
                num_commits,commit_lines = get_commit_lines(version_lines)
                if num_lines != 0:
                    changes_found += 1
                    if num_lines < 50:
                        sum_change_lines += num_lines
                    f_log.write(str(num_lines)+' version changes!\n')
                    f_log.write(version_lines+'\n\n')
                    f_commit_log.write('Benchmark-'+benchmark+'\n'+commit_lines)
            except (Exception) as e:
                p.kill()
                print(str(e))
                f_log.write(str(e)+'\n')
    f_log.write('Files Scanned = '+str(files_scanned)+'\n')
    f_log.write('Changes Found = '+str(changes_found)+'\n')
    if changes_found != 0:
        f_log.write('Average Changes per file = '+str(sum_change_lines/changes_found))
    else:
        f_log.write('Average Changes per file = '+str(0))
    f_log.close()
    f_commit_log.close()



def main():
    #scan_revisions('/Users/nishanthsivakumar/Documents/libcompat/project_repo/maven_projects/')
    get_commit_history()

if __name__ == '__main__':
    main()
