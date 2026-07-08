# Catalogue

## Files description
File format: 'Trulux_app'+'script name'.py(ipynb)

### 1. Collect external catalogue data

#### 1.1 Chrono24

### 2. Watch Catalogue

With collected data in mongoDB:
- listings
- models

Process further to optimize catalogue

####3. Process

Script 0m:
Description-watch data from chrono24 is converted to all models json file in mongo.
Input-raw watch data from site chrono24,refnum_list(in case of update).
Output names-model_links_listings,model_links_listingsold(in case of update),main image files for each watch model.

Script 0l:
Description-information from chrono models file is converted to models listings collection in mongo.
Input names-urls_listnew(in case of update),model_links_listings.
Output name-listings.

Script globinp:
Description-service function.
Input names-model_links_listings,model_links_listingsold(in case of update),listings.
Output names-urls_listnew,refnum_list,urls_dropped,dicrefnum_drop(in case of update),table_of_models,table_of_brandsinloops,table_of_brands,model_links_listings(in case of update).

Script 1: 
Description- json file that consists of models and json file that consists of all model listings of chrono24 data are converted to intermediate:cleaned preprocessed  json files of models and models listings for each of brands(variable BRND) and after to final:catalog file with chrono24 data for each of brands.
Input names- model_links_listings,listings.
Intermediate output names format-mongopre_modelsv1,mongopre_listingsdef+brand name in low register+v1.
Final output name format- brand name in low register+_cataloguev1.

Script 2: 
Same description as in Script 1 but for each of the variants and also is created variant mapping for sub reference numbers for each of brands..
Input-the same as in Script 1.
Intermediate output names format-mongopre_listingsonvar+brand name in low register+variant  name in low register+v1,map_subrefnew+brand name in low register+v1.
Final output names format- withvar_+brand name in low register+variant  name in low register_cataloguev1,subref_+brand name in low register+variant  name in low register+_cataloguev1.

Script 3:
Description-row data from bezel site are converted to dictionaries in mongo.
Input-no files from mongo,api with bezel site..
Output name format-dict1b+brand name in low register.

Script 4-Description--bezel dictionaries and hodinkee data are added to chrono24 catalog,row data from hodinkee site are converted to dictionaries in mongo previously.
Input names format-brand name in low register+_cataloguev1,dict1b+brand name in low register,api with hodinkee site.
Intermediate output names format-dict+model counter+brand name in low register,model counter range is from 1 to number of models in brand plus 1.
Final output name format-brand name in low register+_cataloguev2.

Script calib:
Description-caliber data from the site caliber corner is collected and converted to mongo.
Input-raw data from caliber site.
Output name-caliber_base_new.

Script 5:Description-caliber data from mongo is added to the catalog that contains chrono24,hodinkee,bezel watch information.
Input names format-
caliber_base_new,brand name in low register+_cataloguev2,map_subrefnew+brand name in low register+v1.
Output name format-brand name in low register+_cataloguev3.

*In the brand name,characters ‘&’,‘ö’,’è’,’ü’,’- ‘,’.’ and space characters are deleted.


Sequence of containers running:

1.Script 0m.

2.Script 0l.

3.Script globinp.

4.Scripts 1 for each brand in list of brands-in parallel.

5.Scripts 2 for each brand in list of brands-in parallel.

6.Scripts 3 for each brand in list of brands-in parallel.

7.Scripts 4 for each brand in list of brands-in parallel.

8.Script calib.

9.Scripts 5 for each brand in list of brands- in parallel.

Stages 1,2,3,4+5,6,7,8,9 to run in series.

Stage 8 can be run in parallel with other stages.

Stages 4 and 5 in 4+5 to run in parallel.

Variable Multi with value True says “run script or container in parallel with all brands”.

Variable Multi with value False says “run script or container with replacement value of BRND”

In the use case here value of Multi=False.

Quantity of parallel runs in stages 4,5,6,7,9 is quantity of brands in list.

## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

- [ ] [Create](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#create-a-file) or [upload](https://docs.gitlab.com/ee/user/project/repository/web_editor.html#upload-a-file) files
- [ ] [Add files using the command line](https://docs.gitlab.com/ee/gitlab-basics/add-file.html#add-a-file-using-the-command-line) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/trulux-group/catalogue.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

- [ ] [Set up project integrations](https://gitlab.com/trulux-group/catalogue/-/settings/integrations)

## Collaborate with your team

- [ ] [Invite team members and collaborators](https://docs.gitlab.com/ee/user/project/members/)
- [ ] [Create a new merge request](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html)
- [ ] [Automatically close issues from merge requests](https://docs.gitlab.com/ee/user/project/issues/managing_issues.html#closing-issues-automatically)
- [ ] [Enable merge request approvals](https://docs.gitlab.com/ee/user/project/merge_requests/approvals/)
- [ ] [Set auto-merge](https://docs.gitlab.com/ee/user/project/merge_requests/merge_when_pipeline_succeeds.html)

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
