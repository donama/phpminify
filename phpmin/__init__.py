# Copyright 2011 Christian Amaonwu <ozala24@yahoo.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# file extensions to be searched for
PHP_ALLOWED_EXTENSIONS=['php','inc']

# list of php variables to be left untouched
PHP_EXCLUDED_VARIABLES=['_SERVER','_POST','_GET','_COOKIE','_FILES','_ENV','GLOBALS','this-','this']

# list of php functions to be excluded,we could do better than this 
PHP_EXCLUDED_FUNCTIONS=['__construct','__destruct','__call','__toString','count','extract','curl_init','curl_setopt']


import re

import os

import types

from collections import deque

PHP_VARIABLE_REGEX=re.compile(r'\$([a-zA-Z0-9_\-\:]+)')

PHP_FUNCTION_REGEX=re.compile(r'(.*?)(function\s[a-zA-Z0-9_\:\-]+)')



class PHPFileMinify(object):
    """
    Minifies a given php file and return it minified
    content as streams that can be saved to a file or
    printed
    """
        
    def __init__(self,infile=None,outfile=None,scheme=1):
        
        self.infile=infile
        
        self.outfile=outfile
        
        self.scheme=scheme
        
        self.current_file=None;
        
        self.original_size=0
        
        self.compressed_size=0
        
        self.compression_in_percentage=0
        
        self.original_contents=[]
        
        self.compressed_contents=[]
        
        self.current_variables=[]
        
        self.current_functions=[]
        
        self.minified=0
        
        self.streams=''
        
    
    def save_file(self):
        """
        Saves the compressed files
        """
        if self.scheme>1:
            #we are doing maximum compression - substituting function names and variable names
            
            self._substitute_php_functions()
            
            self._sub_php_variables()
            
            self._save_content(self.streams)
        
        else:
            
            self._save_content(self.compressed_contents)
            
    
    def get_compressed_content(self):
        """
        Return the compressed content
        """
        
        return ''.join(self.compressed_contents)
        
    def get_original_content(self):
        """
        Return the original content
        """
        
        return ''.join(self.original_contents)
    
    def _scan_php_variables(self):
        """
        Scans a given file for all the php variables
        used in it
        """
        
        self.current_variables=[]
        
        variables=[]
        
        if self.current_file:
            
            variables=PHP_VARIABLE_REGEX.findall(self.current_file)
            
            if len(variables):
                
                variables=[c for c in variables if c not in PHP_EXCLUDED_VARIABLES]
                
                if len(variables):
                    
                    variables=list(set(variables))
                    
                    self.current_variables=variables
                    
                    PHPApplicationMinify.VARIABLE_LISTS.extend(variables)
                    
                    PHPApplicationMinify.VARIABLE_LISTS=list(set(PHPApplicationMinify.VARIABLE_LISTS))
        
    def _scan_php_functions(self):
        """
        Scans a given file for all the user defined php
        functions
        """
        
        self.current_functions=[]
        
        functions=[]
        
        if self.current_file:
            
            functions=PHP_FUNCTION_REGEX.findall(self.current_file)
            
            if len(functions):
                
                for extra,func in functions:
                    
                    if func:
                        
                        func=func.split(' ')
                        
                        if len(func):
                            
                            self.current_functions.append(func[1])
                            
            if len(self.current_functions):
                
                PHPApplicationMinify.FUNCTION_LISTS.extend(list(set(self.current_functions)))
                
                PHPApplicationMinify.FUNCTION_LISTS=list(set(PHPApplicationMinify.FUNCTION_LISTS))
                    
                
    def _generate_php_variable_maps(self):
        """
        Builds a map of php variables with its replacement
        """
        if len(self.current_variables)==0:
            
            return
        
        b='abcdefghijklmnopqrstuvwxyz'
        
        maps=list(b)
        
        delta=len(maps)-len(self.current_variables)- len(PHPApplicationMinify.VARIABLE_LISTS)
        
        vlists=[]
        
        if delta<0:
            
            expansion=range(abs(delta))
            
            for k in expansion:
                
                m=maps[k]+str(k)
                
                vlists.append(m)
                
        else:
            
            vlists=maps
            
        
        for term in self.current_variables:
            
            if len(term)>1 and not term.endswith("-"):
                
                for n in vlists:
                    
                    
                    if not PHPApplicationMinify.VARIABLE_MAPS.has_key(term) and n not in PHPApplicationMinify.VARIABLE_MAPS.values():
                        
                        PHPApplicationMinify.VARIABLE_MAPS[term]=n
                        break
                    
                continue
        
        
    def _sub_php_variables(self):
        """
        Substitutes all found user defined php variables
        in a given file with shorter generated ones
        """
    
        #Do variable substitution
        
        if len(PHPApplicationMinify.VARIABLE_MAPS)==0:
            
            return
        
        for old_name,new_name in PHPApplicationMinify.VARIABLE_MAPS.items():
            
            self.streams=re.sub(r'\b%s\b'%old_name,new_name,self.streams)
            
    def _generate_php_function_maps(self):
        """
        Generates a lists of user defined php functions with its
        replacement options
        """
        
        fs=['fn0','fn1','fn2','fn3','fn4','fn5','fn6','fn7','fn8','fn9']
        
        delta=0
        
        if len(self.current_functions)==0:
            
            return
        
        delta=len(fs)- len(self.current_functions)- len(PHPApplicationMinify.FUNCTION_LISTS)
        
        flists=[]
        
        if delta<0:
            
            expansion=range(abs(delta))
            
            for k in expansion:
                
                m='fn'+str(k)
                
                flists.append(m)
                
                
        else:
            
            flists=fs
        
        for fn in self.current_functions:
            
            if fn not in PHP_EXCLUDED_FUNCTIONS:
                
                for n in flists:
                    
                    if not PHPApplicationMinify.FUNCTION_MAPS.has_key(fn) and n not in PHPApplicationMinify.FUNCTION_MAPS.values():
                        
                        PHPApplicationMinify.FUNCTION_MAPS[fn]=n
                        break
                    
                continue
        
    def _substitute_php_functions(self):
        """
        Substitutes all found user defined php functions with
        shorter names that are automatically generated
        """
    
        #do the substitutioning
        
        if len(PHPApplicationMinify.FUNCTION_MAPS)==0:
            
            return
        
        for old_name,new_name in PHPApplicationMinify.FUNCTION_MAPS.items():
            
            self.streams=re.sub(r'%s'%old_name,new_name,self.streams)
            
    def process_report(self):
        """
        Generates compresion report
        """
        
        if self.original_size==0:
            
            pc=0
        else:
            
            pc=(float(self.original_size)- float(self.compressed_size))/float(self.original_size)
            
        tpl="Status - File : %s compressed - OSize : %.2f kb - CSize : %.2f kb PR : %.2f "%(os.path.basename(self.infile),(float(self.original_size)/1000.00),(float(self.compressed_size)/1000.00),float(pc)*100.00)
        
        return tpl
    
    def is_minified(self):
        """
        Returns status on file compression report
        """
        return self.minified
    
    def _parse_file(self):
        """
        Does the dirty work of parsing file content and doing the compression
        """
        
        if len(self.original_contents)==0:
            
            return
        
        for line in self.original_contents:
            
            if line is not None:
                
                line=line.strip()
                
                if line.startswith("#") or line.startswith("/*") or line.startswith("*") or line.startswith("//") or line.startswith('/') or line.startswith("|") or line.startswith("-") or line.startswith(".-") or line.startswith("'-"):
                    
                    continue
                
                else:
                    
                    self.compressed_contents.append(line)
        
        
        if len(self.compressed_contents):
            
            self.compressed_contents=[c+' ' for c in self.compressed_contents if len(c)>0]
            
        
        if self.scheme>1 and len(self.compressed_contents):
            # Maximum compression mode
            self.streams=' '.join(self.compressed_contents)
            
            #Scan for all php variables in the streams
            
            self._scan_php_variables()
            
            #scan for all php user defined functions
            
            self._scan_php_functions()
            
            #Generate php variable maps
            self._generate_php_variable_maps()
            
            #Generate php function maps
            self._generate_php_function_maps()
            
            
        else:
            pass
        
    
    def _save_content(self,data=None):
        """
        Try savind contents depending on its type
        """
        if data is None:
            
            return
        
        
        try:
            
            f=open(self.outfile,'wb')
            
            if f:
                
                if type(data)==types.ListType:
                    
                    f.writelines(data)
                
                else:
                    
                    f.write(data)
            
            f.close()
            
            if os.path.exists(self.outfile):
                
                self.compressed_size=os.path.getsize(self.outfile)
                
                self.minified=1
        
        except IOError,e:
            
            pass
            
            
    def minify(self):
        """
        A public interface for performing file content
        minification
        """
        
        if self.infile is not None:
            
            self.original_size=os.path.getsize(self.infile)
            
            try:
                
                h=open(self.infile,'rb')
                
                
                if h:
                    
                    self.current_file=h.read()
                    
                    self.original_contents=self.current_file.splitlines()
                    
                self._parse_file()
                
                h.close()
            
            except IOError,e:
                
                h.close()
                
                pass
        
        

class PHPApplicationMinify(object):
    """
    Minifies an entire php application directory by walking
    the application folders and minifying each pure php
    files found. It tries to maintain the application
    structure in the minified version of the application but do
    exclude files such as css, js and images etc even though the directory
    structures are created.
    """
    
    FUNCTION_LISTS=[]
    
    VARIABLE_LISTS=[]
    
    VARIABLE_MAPS={}
    
    FUNCTION_MAPS={}
    
    def __init__(self,appdir=None,outputdir=None,scheme=1):
        
        self.local_tree={}
        
        self.rootdir=None
        
        self.directory_tree={}
        
        self.scheme=scheme
        
        self.appdir=appdir
        
        self.app_folder_count=0
        
        self.app_file_count=0
        
        self.files=deque()
        
        if outputdir is None:
            
            self.outputdir='appsminify'
            
        else:
            
            self.outputdir=outputdir
    
    
    def _generate_application_directory_tree(self):
        """
        Walks the application folder and generates
        a map of the folders and files found in each
        folder
        """
    
        if self.appdir is not None:
            
            for directory_path,directory_lists,file_lists in os.walk(self.appdir):
                
                self.app_folder_count+=1
                
                self.app_file_count+=len(file_lists)
                
                self._build_directory_files_map(os.path.abspath(directory_path),file_lists)
        
    
    def _build_directory_files_map(self,dirpath=None,file_lists=[]):
        """
        Maps each directory in the application folder to a lists of files
        found inside it
        """
        
        if dirpath is None or dirpath.startswith('.'):
            
            return
        
        if self.rootdir is None:
            
            self.rootdir=dirpath
        
        if not self.local_tree.has_key(dirpath):
            
            self.local_tree[dirpath]=file_lists
        
        return
    
    def minify_app(self):
        """
        Starts minifying the application files
        """
        
        self._generate_application_directory_tree()
        
        if self.rootdir and self.outputdir:
            
            if self.rootdir.endswith('/'):
                
                self.rootdir=self.rootdir[:-1]
                
            outputdir=os.path.join(os.path.dirname(self.rootdir),self.outputdir)
            
            if not os.path.exists(outputdir):
                
                try:
                    
                    os.makedirs(outputdir)
                
                except IOError,e:
                    
                    print "PHPApplicationMinify could not create the output directory : %s"%outputdir
                    
                    return
            
            
            
            self._compress_files()
            
            self.statistics()
        
    
    def _compress_files(self):
        """
        Starts off the compression process, may take a while
        depending on the size of the files in the application and the number
        of folders found
        """
        
        if len(self.local_tree)==0:
            
            return
        
        outdir=os.path.join(os.path.dirname(self.rootdir),self.outputdir)
        
        for directory_path,file_lists in self.local_tree.items():
            
            savedir=None
            
            if directory_path.endswith("/"):
                
                directory_path=directory_path[:-1]
                
            if directory_path==self.rootdir:
                
                savedir=os.path.join(os.path.dirname(self.rootdir),self.outputdir)
            
            else:
                
                targetdir=directory_path.replace(self.rootdir,outdir)
                
                if targetdir is not None:
                    
                    savedir=targetdir
            
            if not os.path.exists(savedir):
                
                try:
                    
                    os.makedirs(savedir)
                
                except IOError,e:
                    
                    pass
            
            if len(file_lists):
                
                for filename in file_lists:
                    
                    if filename and os.path.splitext(filename)[1][1:] in PHP_ALLOWED_EXTENSIONS:
                        
                        infile=os.path.join(directory_path,filename)
                        
                        outfile=os.path.join(savedir,filename)
                        
                        if os.path.isfile(infile):
                            
                            file_object=PHPFileMinify(infile,outfile,self.scheme)
                            
                            file_object.minify()
                            
                            self.files.append((file_object,outfile))
                            
                
        if len(self.files):
                    
            for fh,fd in self.files:
                        
                fh.save_file()
                        
                if fh.is_minified():
                            
                    if not self.directory_tree.has_key(fd):
                                    
                        self.directory_tree[fd]=fh.process_report();
                        
                        
                
            
    def statistics(self):
        """
        Generates process statistics
        """
        
        print '-'*50
        
        print 'Application  contains %s folders and %s files :'%(str(self.app_folder_count),str(self.app_file_count))
        
        print '-'*50
                
        print ''
        
        print ' Generating minification status:'
        
        print ''
        
        for dir,status in self.directory_tree.items():
            
            print "%s --> %s"%(dir,status)
        
        print'-'*50
        
        
